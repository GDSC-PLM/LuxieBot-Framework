import motor

from db.interfaces.i_user_repo import IUserRepository

class MongoUserRepository(IUserRepository):
    def __init__(self,  collection: motor.motor_asyncio.AsyncIOMotorCollection):
        self.collection = collection
        
    async def initialize(self) -> None:
        await self.collection.create_index("discord_id", unique=True, sparse=True)
        await self.collection.create_index("standoff2_id", unique=True, sparse=True)
        await self.collection.create_index("nexsplit_uid", unique=True)

    async def get_user_by_discord(self, discord_id: str):
        return await self.collection.find_one({"discord_id": discord_id})

    async def get_user_by_standoff2(self, standoff2_id: str):
        return await self.collection.find_one({"standoff2_id": standoff2_id})

    async def get_user_by_nexsplit(self, nexsplit_uid: str):
        return await self.collection.find_one({"nexsplit_uid": nexsplit_uid})
    
    async def get_id_by_query(self, query: dict, target_field: str) -> str | None:
        clauses = [{k: v} for k, v in query.items() if v]
        if not clauses: 
            return None
            
        doc = await self.collection.find_one({"$or": clauses}, {target_field: 1, "_id": 0})
        return doc.get(target_field) if doc else None

    async def create_user(self, discord_id: str, standoff2_id: str, nexsplit_uid: str, pin_hash: str):
        await self.collection.insert_one({
            "discord_id": discord_id,
            "standoff2_id": standoff2_id,
            "nexsplit_uid": nexsplit_uid,
            "pin_hash": pin_hash
        })
        
    async def update_nexsplit_user_links(self, user_id, discord_id: str, standoff2_id: str, pin_hash: str):
        await self.collection.update_one( 
            {"_id": user_id}, 
            {"$set": { 
                "discord_id": discord_id, 
                "standoff2_id": standoff2_id, 
                "pin_hash": pin_hash 
            }} 
        )
        
    async def bind_discord_to_user(self, user_id, new_discord_id: str):
        """Binds a new Discord ID to an existing user account during a reclaim."""
        await self.collection.update_one(
            {"_id": user_id}, 
            {"$set": {"discord_id": new_discord_id}}
        )

    async def update_discord_user_links(self, user_id, standoff2_id: str, nexsplit_uid: str, pin_hash: str):
        """Binds Standoff 2 and Nexsplit UIDs to an existing Discord user."""
        await self.collection.update_one( 
            {"_id": user_id}, 
            {"$set": { 
                "standoff2_id": standoff2_id, 
                "nexsplit_uid": nexsplit_uid, 
                "pin_hash": pin_hash 
            }} 
        )
        
    async def unlink_user_targets(self, user_id, remove_discord: bool, remove_standoff: bool):
        """Nullifies specific platform links for a user by completely removing the fields."""
        unset_fields = {}
        
        if remove_discord:
            unset_fields["discord_id"] = ""
        if remove_standoff:
            unset_fields["standoff2_id"] = ""
            
        if unset_fields:
            await self.collection.update_one({"_id": user_id}, {"$unset": unset_fields})
            
    async def delete_user_by_id(self, user_id):
        result = await self.collection.delete_one({"_id": user_id})
        return result.deleted_count > 0