import datetime
import secrets
import os
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import httpx
from pydantic import BaseModel

security = HTTPBearer()

def verify_api_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    expected_token = os.getenv('APITOKEN')
    if not secrets.compare_digest(credentials.credentials, expected_token):
        raise HTTPException(status_code=401, detail="Invalid or missing API Token")
    return credentials.credentials

router = APIRouter(prefix="/api", tags=["Nexsplit Dashboard API"])

class OAuthCallback(BaseModel):
    code: str

@router.post("/auth/discord/callback", tags=["Authentication"])
async def discord_oauth_callback(payload: OAuthCallback):
    """Exchanges Discord code for an access token and returns a session JWT."""
    client_id = os.getenv("CLIENTID")
    client_secret = os.getenv("CLIENTSECRET")
    redirect_uri = os.getenv("REDIRECTAPIURI")
    jwt_secret = os.getenv("JWTSECRET")

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://discord.com/api/oauth2/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "code": payload.code,
                "redirect_uri": redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid Discord Auth Code")
            
        token_data = token_res.json()
        access_token = token_data.get("access_token")

        user_res = await client.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch Discord user")
            
        discord_user = user_res.json()
        discord_id = discord_user.get("id")


    expiration = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)
    jwt_payload = {
        "sub": discord_id,
        "access_token": access_token,
        "exp": expiration
    }
    
    session_token = jwt.encode(jwt_payload, jwt_secret, algorithm="HS256")
    
    return {
        "token": session_token,
        "user": {
            "id": discord_id,
            "username": discord_user.get("username"),
            "avatar": discord_user.get("avatar")
        }
    }

def verify_user_session(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Validates the JWT session token provided by the React web client."""
    jwt_secret = os.getenv("JWTSECRET")
    token = credentials.credentials
    
    try:
        decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        discord_id = decoded.get("sub")
        access_token = decoded.get("access_token")
        
        if not discord_id:
            raise ValueError("Invalid token payload")
            
        return {"discord_id": discord_id, "access_token": access_token}
        
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError) as e:
        raise HTTPException(status_code=401, detail=f"Session Invalid or Expired: {str(e)}")



@router.get("/test")
async def test():
    return "Hello, world!"