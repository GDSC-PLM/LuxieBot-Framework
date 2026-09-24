from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class IPlayerRepository(ABC):

    @abstractmethod
    async def initialize(self) -> None:
        pass
        
    @abstractmethod
    async def get_player_by_nexsplit(self, nexsplit_uid: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_player_mmr(self, nexsplit_uid: str) -> int:
        pass
    
    @abstractmethod
    async def get_all_player_profiles(self, nexsplit_uid: str) -> int:
        pass

    @abstractmethod
    async def update_player_mmr(self, nexsplit_uid: str, points: int) -> int:
        pass

    @abstractmethod
    async def create_player(self, nexsplit_uid: str, guild_id: str, mmr: int) -> None:
        pass

    @abstractmethod
    async def delete_player(self, nexsplit_uid: str, guild_id: str = None) -> bool:
        pass