import motor.motor_asyncio
import pymongo
from db.interfaces.i_player_repo import IPlayerRepository

class MongoPlayerRepository(IPlayerRepository):
    def __init__(self, collection: motor.motor_asyncio.AsyncIOMotorCollection):
        self.collection = collection

    async def initialize(self):
        await self.collection.create_index(
            [("nexsplit_uid", pymongo.ASCENDING), ("guild_id", pymongo.ASCENDING)], 
            unique=True
        )
        await self.collection.create_index("mmr", sparse=True)

    async def get_player_by_nexsplit(self, nexsplit_uid: str):
        return await self.collection.find_one({"nexsplit_uid": nexsplit_uid})

    async def get_player_mmr(self, nexsplit_uid: str) -> int:
        player = await self.collection.find_one(
            {"nexsplit_uid": nexsplit_uid}, 
            {"mmr": 1, "_id": 0}
        )
        return player.get("mmr", 0) if player else 0

    async def get_all_player_profiles(self, nexsplit_uid: str):
        """Fetches all server profiles for a specific player."""
        cursor = self.collection.find(
            {"nexsplit_uid": nexsplit_uid}, 
            {"guild_id": 1, "mmr": 1, "_id": 0}
        )
        return await cursor.to_list(length=100)

    async def update_player_mmr(self, nexsplit_uid: str, points: int):
        result = await self.collection.update_one(
            {"nexsplit_uid": nexsplit_uid}, 
            {"$inc": {"mmr": points}}, 
            upsert=True
        )
        return result.modified_count

    async def create_player(self, nexsplit_uid: str, guild_id: str, mmr: int):
        await self.collection.insert_one({
            "nexsplit_uid": nexsplit_uid,
            "guild_id": guild_id,
            "mmr": mmr
        })

    async def delete_player(self, nexsplit_uid: str, guild_id: str = None):
        query = {"nexsplit_uid": nexsplit_uid}
        if guild_id:
            query["guild_id"] = guild_id
        result = await self.collection.delete_many(query)
        return result.deleted_count > 0
