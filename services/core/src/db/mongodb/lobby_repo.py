import motor
import pymongo

from db.interfaces.i_lobby_repo import ILobbyRepository
from datetime import datetime, timezone

class MongoLobbyRepository(ILobbyRepository):
    def __init__(self, collection: motor.motor_asyncio.AsyncIOMotorCollection):
        self.collection = collection
        
    async def initialize(self) -> None:
        """Initializes the collection with necessary indexes for fast lookup and cleanup."""
        await self.collection.create_index("lobby_id", unique=True)
        await self.collection.create_index("host_nexsplit_uid")

    async def create_lobby(self, lobby_id: str, host_nexsplit_uid: str, guild_id: str, is_global: bool = False, max_players: int = 10, region: str = "EU") -> bool:
        """Creates a new game lobby scoped to a guild or set to global."""
        try:
            await self.collection.insert_one({
                "lobby_id": lobby_id,
                "guild_id": guild_id,
                "is_global": is_global,
                "host_nexsplit_uid": host_nexsplit_uid,
                "players": [host_nexsplit_uid],
                "max_players": max_players,
                "region": region,
                "status": "waiting",
                "created_at": datetime.now(timezone.utc)
            })
            return True
        except Exception as e:
            print(f"Error creating lobby {lobby_id}: {e}")
            return False

    async def get_lobby_by_id(self, lobby_id: str) -> dict:
        """Fetches all data for a specific lobby."""
        return await self.collection.find_one({"lobby_id": lobby_id})

    async def get_active_lobbies_by_region(self, region: str):
        """Fetches a list of all lobbies in a region that are still waiting for players."""
        cursor = self.collection.find({"region": region, "status": "waiting"})
        return await cursor.to_list(length=100)

    async def join_lobby(self, lobby_id: str, nexsplit_uid: str) -> str:
        """
        Safely adds a player to a lobby using atomic operations.
        Returns status string: 'joined', 'full', or 'not_found'.
        """
        lobby = await self.get_lobby_by_id(lobby_id)
        if not lobby:
            return "not_found"
            
        if len(lobby.get("players", [])) >= lobby.get("max_players", 10):
            return "full"

        await self.collection.update_one(
            {"lobby_id": lobby_id},
            {"$addToSet": {"players": nexsplit_uid}}
        )
        return "joined"

    async def leave_lobby(self, lobby_id: str, nexsplit_uid: str) -> str:
        lobby = await self.collection.find_one({"lobby_id": lobby_id})
        if not lobby: return "not_found"

        await self.collection.update_one(
            {"lobby_id": lobby_id},
            {
                "$pull": {
                    "players": nexsplit_uid,
                    "start_votes": nexsplit_uid,
                    "end_votes": nexsplit_uid,
                    "cancel_votes": nexsplit_uid
                }
            }
        )

        updated_lobby = await self.collection.find_one({"lobby_id": lobby_id}, {"players": 1, "host_nexsplit_uid": 1, "status": 1, "_id": 0})
        remaining_players = updated_lobby.get("players", [])
        current_status = updated_lobby.get("status", "waiting")

        if not remaining_players:
            if current_status in ["waiting", "finished", "cancelled"]:
                await self.delete_lobby(lobby_id)
                return "lobby_deleted"
            return "player_left"

        if lobby.get("host_nexsplit_uid") == nexsplit_uid:
            await self.collection.update_one(
                {"lobby_id": lobby_id},
                {"$set": {"host_nexsplit_uid": remaining_players[0]}}
            )
            return "host_transferred"

        return "player_left"

    async def update_lobby_status(self, lobby_id: str, status: str) -> bool:
        """Updates the match engine lifecycle status (e.g., changing 'waiting' to 'active')."""
        result = await self.collection.update_one(
            {"lobby_id": lobby_id},
            {"$set": {"status": status}}
        )
        return result.modified_count > 0

    async def vote_to_start_match(self, lobby_id: str, voter_uid: str) -> dict:
        """Registers a start vote. Starts immediately if 5 votes are logged."""
        result = await self.collection.find_one_and_update(
            {"lobby_id": lobby_id, "status": "waiting", "players": voter_uid},
            {"$addToSet": {"start_votes": voter_uid}},
            return_document=pymongo.ReturnDocument.AFTER
        )
        if not result:
            return {"success": False, "reason": "Lobby not eligible or player not inside."}

        vote_count = len(result.get("start_votes", []))
        if vote_count >= (len(result.get("players", [])) // 2) + 1:
            await self.collection.update_one(
                {"lobby_id": lobby_id},
                {"$set": {"status": "active"}, "$unset": {"start_votes": "", "cancel_votes": ""}}
            )
            return {"success": True, "action": "match_started", "votes": vote_count}

        return {"success": True, "action": "vote_registered", "votes": vote_count}


    async def vote_to_end_match(self, lobby_id: str, voter_uid: str, is_staff: bool = False) -> dict:
        """Ends the match. Executed instantly if is_staff=True, otherwise requires 5 votes."""
        if is_staff:
            result = await self.collection.update_one(
                {"lobby_id": lobby_id, "status": "active"},
                {"$set": {"status": "finished"}, "$unset": {"end_votes": "", "cancel_votes": ""}}
            )
            if result.modified_count > 0:
                return {"success": True, "action": "match_ended", "forced_by_staff": True}
            return {"success": False, "reason": "Lobby not found or match is not active."}

        result = await self.collection.find_one_and_update(
            {"lobby_id": lobby_id, "status": "active", "players": voter_uid},
            {"$addToSet": {"end_votes": voter_uid}},
            return_document=pymongo.ReturnDocument.AFTER
        )
        if not result:
            return {"success": False, "reason": "Lobby not eligible or player not inside."}

        vote_count = len(result.get("end_votes", []))
        if vote_count >= (len(result.get("players", [])) // 2) + 1:
            await self.collection.update_one(
                {"lobby_id": lobby_id},
                {"$set": {"status": "finished"}, "$unset": {"end_votes": "", "cancel_votes": ""}}
            )
            return {"success": True, "action": "match_ended", "votes": vote_count}

        return {"success": True, "action": "vote_registered", "votes": vote_count}


    async def vote_to_cancel_match(self, lobby_id: str, voter_uid: str, is_staff: bool = False) -> dict:
        """Cancels a match. Executed instantly if is_staff=True, otherwise requires 5 votes."""
        if is_staff:
            result = await self.collection.update_one(
                {"lobby_id": lobby_id, "status": {"$in": ["waiting", "active"]}},
                {"$set": {"status": "cancelled"}, "$unset": {"start_votes": "", "end_votes": "", "cancel_votes": ""}}
            )
            if result.modified_count > 0:
                return {"success": True, "action": "match_cancelled", "forced_by_staff": True}
            return {"success": False, "reason": "Lobby not found or already finished."}

        result = await self.collection.find_one_and_update(
            {"lobby_id": lobby_id, "status": {"$in": ["waiting", "active"]}, "players": voter_uid},
            {"$addToSet": {"cancel_votes": voter_uid}},
            return_document=pymongo.ReturnDocument.AFTER
        )
        if not result:
            return {"success": False, "reason": "Lobby not eligible or player not inside."}

        vote_count = len(result.get("cancel_votes", []))
        if vote_count >= (len(result.get("players", [])) // 2) + 1:
            await self.collection.update_one(
                {"lobby_id": lobby_id},
                {"$set": {"status": "cancelled"}, "$unset": {"start_votes": "", "end_votes": "", "cancel_votes": ""}}
            )
            return {"success": True, "action": "match_cancelled", "votes": vote_count}

        return {"success": True, "action": "vote_registered", "votes": vote_count}


    async def delete_lobby(self, lobby_id: str) -> bool:
        """
        Permanently deletes a lobby only if its status is 'waiting' or 'finished'.
        Returns True if deleted, False if not found or if the lobby is 'active'.
        """
        result = await self.collection.delete_one({
            "lobby_id": lobby_id,
            "status": {"$in": ["waiting", "finished", "cancelled"]}
        })
        return result.deleted_count > 0
