import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv('DB_URI')
if not URI:
    raise ValueError("FATAL ERROR: Environment variable 'DB_URI' is not set in .env file.")
client = AsyncIOMotorClient(URI)
db = client["luxie_db"]
user_collection = db["user"]
player_collection = db["player_data"]
match_collection = db["matches"]
lobby_collection = db["lobbies"]