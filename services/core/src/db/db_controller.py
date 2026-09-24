from db.db_factory import db
from typing import Optional, Dict, Any

# User

async def create_user(discord_id: str, standoff2_id: str, nexsplit_uid: str, pin_hash: str) -> None:
    return await db.user_repo.create_user(discord_id, standoff2_id, nexsplit_uid, pin_hash)

async def get_user_by_discord(discord_id: str) -> Optional[Dict[str, Any]]:
    return await db.user_repo.get_user_by_discord(discord_id)

async def get_user_by_standoff2(standoff2_id: str) -> Optional[Dict[str, Any]]:
    return await db.user_repo.get_user_by_standoff2(standoff2_id)

async def get_user_by_nexsplit(nexsplit_uid: str) -> Optional[Dict[str, Any]]:
    return await db.user_repo.get_user_by_nexsplit(nexsplit_uid)

async def get_id_by_query(query: dict, target_field: str) -> str | None:
    return await db.user_repo.get_id_by_query(query, target_field)

async def update_nexsplit_user_links(user_id, discord_id: str, standoff2_id: str, pin_hash: str) -> None:
    return await db.user_repo.update_nexsplit_user_links(user_id, discord_id, standoff2_id, pin_hash)

async def bind_discord_to_user(user_id, new_discord_id: str) -> None:
    return await db.user_repo.bind_discord_to_user(user_id, new_discord_id)

async def update_discord_user_links(user_id, standoff2_id: str, nexsplit_uid: str, pin_hash: str) -> None:
    return await db.user_repo.update_discord_user_links(user_id, standoff2_id, nexsplit_uid, pin_hash)

async def unlink_user_targets(user_id, remove_discord: bool, remove_standoff: bool) -> None:
    return await db.user_repo.unlink_user_targets(user_id, remove_discord, remove_standoff)

async def delete_user_by_id(user_id) -> bool:
    return await db.user_repo.delete_user_by_id(user_id)

# Player
    
async def get_player_by_nexsplit(nexsplit_uid: str) -> Optional[Dict[str, Any]]:
    return await db.player_repo.get_player_by_nexsplit(nexsplit_uid)

async def get_player_mmr(nexsplit_uid: str) -> int:
    return await db.player_repo.get_player_mmr(nexsplit_uid)

async def get_all_player_profiles(nexsplit_uid: str) -> int:
    return await db.player_repo.get_all_player_profiles(nexsplit_uid)

async def update_player_mmr(nexsplit_uid: str, points: int) -> int:
    return await db.player_repo.update_player_mmr(nexsplit_uid, points)

async def create_player(nexsplit_uid: str, guild_id: str, mmr: int) -> None:
    return await db.player_repo.create_player(nexsplit_uid, guild_id, mmr)

async def delete_player(nexsplit_uid: str, guild_id: str = None) -> bool:
    return await db.player_repo.delete_player(nexsplit_uid, guild_id)

# Lobby