from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class IUserRepository(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        pass
    
    @abstractmethod
    async def get_user_by_discord(self, discord_id: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def get_user_by_standoff2(self, standoff2_id: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def get_user_by_nexsplit(self, nexsplit_uid: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def get_id_by_query(self, query: dict, target_field: str) -> str | None:
        pass

    @abstractmethod
    async def create_user(self, discord_id: str, standoff2_id: str, nexsplit_uid: str, pin_hash: str) -> None:
        pass

    @abstractmethod
    async def update_nexsplit_user_links(self, user_id, discord_id: str, standoff2_id: str, pin_hash: str) -> None:
        pass
    
    @abstractmethod
    async def bind_discord_to_user(user_id, new_discord_id: str) -> None:
        pass
    
    @abstractmethod
    async def update_discord_user_links(user_id, standoff2_id: str, nexsplit_uid: str, pin_hash: str) -> None:
        pass
    
    @abstractmethod
    async def unlink_user_targets(user_id, remove_discord: bool, remove_standoff: bool) -> None:
        pass
    
    @abstractmethod
    async def delete_user_by_id(self, user_id) -> bool:
        pass