from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

class ILobbyRepository(ABC):

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the collection with necessary indexes for fast lookup and cleanup."""
        pass

    @abstractmethod
    async def create_lobby(self, lobby_id: str, host_nexsplit_uid: str, max_players: int = 10, region: str = "EU") -> bool:
        """Create a new game lobby with the host added as the first player."""
        pass

    @abstractmethod
    async def get_lobby_by_id(self, lobby_id: str) -> Optional[Dict[str, Any]]:
        """Fetch all data for a specific lobby."""
        pass

    @abstractmethod
    async def get_active_lobbies_by_region(self, region: str) -> List[Dict[str, Any]]:
        """Fetch a list of all lobbies in a region that are still waiting for players."""
        pass

    @abstractmethod
    async def join_lobby(self, lobby_id: str, nexsplit_uid: str) -> str:
        """Safely add a player to a lobby using atomic operations."""
        pass

    @abstractmethod
    async def leave_lobby(self, lobby_id: str, nexsplit_uid: str) -> str:
        """Handle a player exiting the lobby, tracking host transfers and deletions."""
        pass

    @abstractmethod
    async def update_lobby_status(self, lobby_id: str, status: str) -> bool:
        """Update the match engine lifecycle status."""
        pass

    @abstractmethod
    async def vote_to_start_match(self, lobby_id: str, voter_uid: str) -> Dict[str, Any]:
        """Register a start vote and handle immediate match initiation."""
        pass

    @abstractmethod
    async def vote_to_end_match(self, lobby_id: str, voter_uid: str, is_staff: bool = False) -> Dict[str, Any]:
        """End the match instantly via staff override or by logging cumulative votes."""
        pass

    @abstractmethod
    async def vote_to_cancel_match(self, lobby_id: str, voter_uid: str, is_staff: bool = False) -> Dict[str, Any]:
        """Cancel a match instantly via staff override or by logging cumulative votes."""
        pass

    @abstractmethod
    async def delete_lobby(self, lobby_id: str) -> bool:
        """Permanently delete a lobby only if its status is 'waiting' or 'finished'."""
        pass
