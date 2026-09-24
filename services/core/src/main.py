import os # used to load env variables
from pathlib import Path
import time # used for dql
import uuid # random identifiers
import jwt # for access tokens
import orjson # fast json
import asyncio # put heavy tasks to background so it won't block the loop
import logging # yes
import secrets # used to compare env variables
from dotenv import load_dotenv # uses os
from pydantic_settings import BaseSettings, SettingsConfigDict # imports env variables
from pydantic import BaseModel, Field, SecretStr, ValidationError # for strict schematics checking
from contextlib import asynccontextmanager # for fastapi lifespan
import valkey.asyncio as valkey # concurrency + off-load stuff to memory
from api.rest import router as rest_router # custom rest api logic goes here
from fastapi import FastAPI, WebSocket, WebSocketDisconnect # rest api
from fastapi.middleware.cors import CORSMiddleware # lets the react website/dashboard access the server
# from db.db_factory import db # to initialize database
# from api.websockets import ROUTES # custom websocket logic goes here

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

class ServerEnv(BaseSettings):
    token: str = Field(alias="API_TOKEN")
    header: str = Field(alias="CLIENT_HEADER")
    valkey_url: str = Field(alias="VALKEY_URL")
    jwt_secret: SecretStr = Field(alias="JWT_SECRET")
    origins: str = Field(alias="ORIGINS")
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        extra="ignore"
    )

class BasePayload(BaseModel):
    action: str
    interaction_id: str 

class HandshakePayload(BasePayload):
    token: str

class DistributedRateLimiter:
    """Sliding-window rate limiter utilizing a distributed Valkey cluster."""
    def __init__(self, valkey_client: valkey.Valkey, max_actions: int = 25, timeframe: float = 1.0):
        self.vk = valkey_client
        self.max_actions = max_actions
        self.timeframe = timeframe
        
        self.lua_script = """
        -- KEYS[1]: the specific rate limit key for this client
        -- ARGV[1]: current timestamp (used as both score and member)
        -- ARGV[2]: the cutoff timestamp (now - timeframe)
        -- ARGV[3]: max allowed actions
        -- ARGV[4]: TTL for the key in seconds

        server.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', ARGV[2])
        local current_count = server.call('ZCARD', KEYS[1])
        server.call('EXPIRE', KEYS[1], ARGV[4])
        if tonumber(current_count) < tonumber(ARGV[3]) then
            server.call('ZADD', KEYS[1], ARGV[1], ARGV[1])
            return 1 -- Allowed
        else
            return 0 -- Blocked
        end
        """

    async def is_allowed(self, client_id: str) -> bool:
        """Determines if a client is within their allowed action threshold."""
        key = f"rate_limit:{client_id}"
        now = time.time()
        clear_before = now - self.timeframe
        ttl = int(self.timeframe) + 2
        
        result = await self.vk.eval(
            self.lua_script, 
            1,                # number of keys being passed
            key,              # KEYS[1]
            now,              # ARGV[1]
            clear_before,     # ARGV[2]
            self.max_actions, # ARGV[3]
            ttl               # ARGV[4]
        )
        
        return bool(result)

class Server:
    "The brain. You don't have to touch this unless you now what you're doing. Implement custom logic at 'root/core/api'. :D"
    def __init__(self, env: ServerEnv):
        load_dotenv()
        self.TOKEN = env.token
        self.HEADER = env.header
        self.VALKEYURL = env.valkey_url
        self.JWTSECRET = env.jwt_secret.get_secret_value()
        self.ORIGINS = env.origins.split(",") if env.origins else []
        if not self.TOKEN or not self.HEADER or not self.VALKEYURL or not self.JWTSECRET or not self.ORIGINS:
            raise ValueError("FATAL ERROR: Environment variables are not set or empty in .env file.")
        
        #self.ROUTES = ROUTES
        self.app = FastAPI(lifespan=self.lifespan)
        self.app.include_router(rest_router)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"], # do NOT allow other methods unless explicitly defined in the codebase
            allow_headers=["Client-ID", "Authorization"], # same for headers
        )
        self.app.add_api_websocket_route("/ws", self.websocket_endpoint)
        self.app.state.ws_server = self
        self.instance_id = str(uuid.uuid4())
        self.CHANNELNAME = f"ws_instance:{self.instance_id}"
        self.local_connections = {}
        self.vk = None
        self.limiter = None
        self.pubsub_task = None
        
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        logging.info("Initializing database indexes...")
        #await db.initialize_all()
        logging.info("Connecting to Valkey...")
        self.vk = valkey.from_url(self.VALKEYURL, decode_responses=True)
        self.limiter = DistributedRateLimiter(self.vk, max_actions=25, timeframe=1.0)
        self.pubsub_task = asyncio.create_task(self._valkey_pubsub_listener())
        self.dlq_cleanup_task = asyncio.create_task(self._dlq_archiver())
        yield
        if self.pubsub_task:
            self.pubsub_task.cancel()
        if self.dlq_cleanup_task:
            self.dlq_cleanup_task.cancel()
        await asyncio.gather(self.pubsub_task, self.dlq_cleanup_task, return_exceptions=True)
        await self.vk.close()
    
    async def _dlq_archiver(self):
        await asyncio.sleep(10)
        
        while True:
            try:
                lock = await self.vk.set("lock:dlq_archiver", self.instance_id, nx=True, ex=300)
                
                if not lock:
                    await asyncio.sleep(60)
                    continue
                    
                async for key in self.vk.scan_iter(match="dlq:*"):
                    while True:
                        messages = []
                        for _ in range(100):
                            msg = await self.vk.lpop(key)
                            if not msg:
                                break
                            messages.append(msg)
                            
                        if not messages:
                            break
                            
                        try:
                            await asyncio.to_thread(self._write_dlq_logs, key, messages)
                            logging.info(f"Archived chunk of {len(messages)} messages from {key}")
                        except Exception as io_err:
                            logging.error(f"Failed to write DLQ logs to disk: {io_err}")
                
                await self.vk.delete("lock:dlq_archiver")
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"DLQ Archiver error: {e}")
                
            await asyncio.sleep(300)
    
    def _write_dlq_logs(self, key: str, messages: list):
        """
        Synchronously writes unrouted Dead Letter Queue (DLQ) messages to disk.
        Executed in a separate thread to prevent blocking the async event loop.
        """
        log_dir = "dlq_archives"
        os.makedirs(log_dir, exist_ok=True)
        
        safe_name = key.replace(":", "_")
        file_path = os.path.join(log_dir, f"{safe_name}.log")
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        with open(file_path, "a", encoding="utf-8") as f:
            for msg in messages:
                msg_str = msg if isinstance(msg, str) else msg.decode("utf-8", errors="replace")
                f.write(f"[{timestamp}] {msg_str}\n")
        
    async def _valkey_pubsub_listener(self):
        """Make multiple instances of the bot talk to each other. Listens ONLY to this specific instance's channel for incoming remote messages."""
        ps = self.vk.pubsub()
        
        while True:
            try:
                await ps.subscribe(self.CHANNELNAME)
                logging.info(f"Instance {self.instance_id} subscribed to routing bus channel: {self.CHANNELNAME}")
                
                async for message in ps.listen():
                    if message["type"] != "message":
                        continue
                    
                    try:
                        packet = orjson.loads(message["data"])
                        target_id = packet.get("target_client_id")
                        payload_data = packet.get("data")
                        
                        target_queue = self.local_connections.get(target_id)
                        if target_queue:
                            try:
                                target_queue.put_nowait(orjson.dumps(payload_data))
                            except asyncio.QueueFull:
                                logging.warning(f"Client {target_id} queue full. Pushing to DLQ.")
                                dlq_key = f"dlq:{target_id}"
                                async with self.vk.pipeline(transaction=True) as pipe:
                                    pipe.rpush(dlq_key, orjson.dumps(payload_data))
                                    pipe.ltrim(dlq_key, -100, -1)
                                    await pipe.execute()
                        else:
                            logging.warning(f"Client {target_id} offline. Pushing to DLQ.")
                            dlq_key = f"dlq:{target_id}"
                            async with self.vk.pipeline(transaction=True) as pipe:
                                pipe.rpush(dlq_key, orjson.dumps(payload_data))
                                pipe.ltrim(dlq_key, -100, -1)
                                await pipe.execute()
                                
                    except Exception as e:
                        logging.error(f"Error distributing message payload over PubSub: {e}")
                        
            except asyncio.CancelledError:
                logging.info("Valkey Pub/Sub listener routine shutdown smoothly.")
                await ps.unsubscribe(self.CHANNELNAME)
                break 
                
            except Exception as e:
                logging.error(f"Valkey Pub/Sub connection lost: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

    async def route_message(self, target_client_id: str, payload_data: dict) -> bool:
        """
        Routes a message to a client, whether they are connected 
        to this specific server instance or another instance in the cluster.
        """
        if target_client_id in self.local_connections:
            try:
                self.local_connections[target_client_id].put_nowait(orjson.dumps(payload_data))
                return True
            except Exception as e:
                logging.error(f"Failed to send local message to {target_client_id}: {e}")
                return False

        target_instance_id = await self.vk.get(f"client_route:{target_client_id}")
        
        if target_instance_id is None:
            dlq_key = f"dlq:{target_client_id}"
            async with self.vk.pipeline(transaction=True) as pipe:
                pipe.rpush(dlq_key, orjson.dumps(payload_data))
                pipe.ltrim(dlq_key, -100, -1)
                await pipe.execute()
        elif target_instance_id:
            packet = {
                "target_client_id": target_client_id,
                "data": payload_data
            }
            await self.vk.publish(f"ws_instance:{target_instance_id}", orjson.dumps(packet))
            return True

        logging.warning(f"Could not route message: Client {target_client_id} is offline or not mapped.")
        return False
    
    async def handle_handshake(self, websocket, payload, interaction_id):
        try:
            data = HandshakePayload(**payload)
        except ValidationError as e:
            await websocket.send_bytes(orjson.dumps({
                        "error": True, 
                        "message": f"Invalid payload format: {e.errors()[0]['msg']}", 
                        "interaction_id": interaction_id
                    }))
            return False
        
        return True
        
    async def websocket_endpoint(self, websocket: WebSocket):
        client_id = None
        logging.info("New WebSocket connection established.")
        
        await websocket.accept()
        
        auth_header = websocket.headers.get("Authorization", "")
        if not secrets.compare_digest(auth_header, f"Bearer {self.TOKEN}"):
            logging.warning("Blocked connection: Invalid Authorization header.")
            await websocket.close(code=1008, reason="Unauthorized")
            return
        
        try:
            first_message = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
            payload = orjson.loads(first_message)
            
            if not isinstance(payload, dict):
                raise ValueError("Handshake payload is not a dictionary")
            
            data = BasePayload(**payload)
            if data.action != 'handshake':
                logging.warning(f"Expected handshake, got: {data.action}")
                await websocket.close(code=1008, reason="Handshake Required First")
                return
            
            token = payload.get("token")
            if not token:
                await websocket.close(code=1008, reason="JWT Required in Handshake")
                return
            
            try:
                decoded = jwt.decode(token, self.JWTSECRET, algorithms=["HS256"])
                decoded_client_id = decoded.get("sub")
                if not decoded_client_id:
                    raise ValueError("JWT missing 'sub' claim")
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError) as e:
                await websocket.close(code=1008, reason=f"Invalid Token: {e}")
                return
            
            success = await self.handle_handshake(websocket, payload, data.interaction_id)
            if not success:
                await websocket.close(code=1008, reason="Database Handshake Rejected")
                return

            client_id = str(decoded_client_id)
            egress_queue = asyncio.Queue(maxsize=100)
            self.local_connections[client_id] = egress_queue
            
            await self.vk.set(f"client_route:{client_id}", self.instance_id)
            logging.info(f"Client {client_id} authenticated and routed to {self.instance_id}.")

            async def socket_writer():
                try:
                    while True:
                        msg = await egress_queue.get()
                        await websocket.send_bytes(msg)
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logging.error(f"Socket writer error for {client_id}: {e}")

            writer_task = asyncio.create_task(socket_writer())

            dlq_key = f"dlq:{client_id}"
            delivered_count = 0
            while True:
                queued_msg = await self.vk.lpop(dlq_key)
                if not queued_msg:
                    break
                
                await websocket.send_bytes(queued_msg)
                delivered_count += 1
                
            if delivered_count > 0:
                logging.info(f"Delivered {delivered_count} DLQ messages to {client_id}")
            
            # dlq_key = f"dlq:{client_id}"
            # while True:
            #     queued_msg = await self.vk.lpop(dlq_key)
            #     if not queued_msg:
            #         break
            #     await websocket.send_bytes(queued_msg)
            #     logging.info(f"Delivered queued DLQ message to {client_id}")
            
        except (asyncio.TimeoutError, orjson.JSONDecodeError, ValidationError, Exception) as e:
            logging.error(f"Handshake failure: {e}")
            await websocket.close(code=1008, reason="Handshake Error")
            return
        
        try:
            while True:
                try:
                    message = await asyncio.wait_for(websocket.receive_text(), timeout=45.0)
                except asyncio.TimeoutError:
                    logging.warning(f"Client {client_id} timed out. Closing ghost socket.")
                    break
                
                # if len(message) > 1048576:  # 1 MB limit
                #     logging.warning(f"Payload from {client_id} exceeded limits.")
                #     continue

                if not await self.limiter.is_allowed(client_id):
                    await websocket.send_bytes(orjson.dumps({
                        "error": True, 
                        "message": "Too many requests. Please slow down.", 
                        "interaction_id": None
                    }))
                    continue
                
                try:
                    payload = orjson.loads(message)
                    if not isinstance(payload, dict):
                        raise ValueError("Payload is not a dictionary")
                    data = BasePayload(**payload)
                    if data.action == "ping":
                        await websocket.send_bytes(orjson.dumps({"action": "pong"}))
                        continue
                except (orjson.JSONDecodeError, ValidationError, ValueError) as e:
                    logging.error(f"Dropped malformed base payload: {e}")
                    continue
                
                action = data.action
                interaction_id = data.interaction_id

                # we can trust the TCP connection enough to not rely on this block, it's just gonna add more load to valkey
                # if not await self.vk.exists(f"client_route:{client_id}"):
                #     await websocket.close(code=1008, reason="Session Invalidated")
                #     return
                    
                handler = self.ROUTES.get(action)
                if handler:
                    try:
                        await handler(websocket, payload, interaction_id)
                    except Exception as e:
                        logging.error(f"Internal Error in handler execution logic {action}: {e}")
                        await websocket.send_bytes(orjson.dumps({
                            "error": True, "message": "Internal server error.", "interaction_id": interaction_id
                        }))
                else:
                    logging.error(f"Unknown action: {action}")
        
        except WebSocketDisconnect:
            logging.info("WebSocket connection closed cleanly.")
        except Exception as e:
            logging.exception("An unexpected WebSocket connection error occurred:")
        finally:
            if 'writer_task' in locals():
                writer_task.cancel()
            
            if client_id:
                self.local_connections.pop(client_id, None)
                lua_script = "if server.call('get', KEYS[1]) == ARGV[1] then return server.call('del', KEYS[1]) else return 0 end"
                await self.vk.eval(lua_script, 1, f"client_route:{client_id}", self.instance_id)
                await self.vk.delete(f"rate_limit:{client_id}")
                
            try:
                await websocket.close()
            except RuntimeError:
                pass

settings = ServerEnv()
server = Server(env=settings)
app = server.app

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000,
        workers=4,
        proxy_headers=True,
        forwarded_allow_ips="*",
        ws_ping_interval=20.0,
        ws_ping_timeout=20.0,
        ws_max_size=1048576
    )