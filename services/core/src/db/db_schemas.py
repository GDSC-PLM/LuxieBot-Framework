from pydantic import Field
from main import BasePayload
from typing import Optional
    
class DiscordUserPayload(BasePayload):
    discord_id: str
    guild_id: str = "GLOBAL"

class LinkAccountPayload(DiscordUserPayload):
    standoff2_id: str = Field(..., min_length=1, max_length=20)
    pin: str = Field(..., pattern=r'^\d{4}$')
    
class UnlinkAccountPayload(BasePayload):
    discord_id: str
    target: str = Field(..., pattern=r'^(discord|standoff2|both)$')
    pin: str = Field(..., pattern=r'^\d{4}$')
    
class DeleteAccountPayload(DiscordUserPayload):
    pin: str = Field(..., pattern=r'^\d{4}$')
    
class ReclaimAccountPayload(BasePayload):
    discord_id: str
    nexsplit_uid: str
    pin: str = Field(..., pattern=r'^\d{4}$')