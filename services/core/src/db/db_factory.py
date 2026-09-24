import os
from dotenv import load_dotenv
from db.db_connections import user_collection, player_collection, lobby_collection
from db.mongodb.player_repo import MongoPlayerRepository
from db.mongodb.lobby_repo import MongoLobbyRepository
from db.mongodb.user_repo import MongoUserRepository
# Import future PostgreSQL/MySQL repos here

load_dotenv()
ENGINE = os.getenv('DB_ENGINE')

if not ENGINE:
    raise ValueError("FATAL ERROR: 'DB_ENGINE' is missing in .env file.")

class DatabaseFactory:
    def __init__(self):
        self.db_engine = ENGINE.lower()
        
        if self.db_engine == "mongodb":
            self.user_repo = MongoUserRepository(user_collection)
            self.player_repo = MongoPlayerRepository(player_collection)
            self.lobby_repo = MongoLobbyRepository(lobby_collection)
            
        elif self.db_engine == "postgres":
            # self.user_repo = PostgresUserRepository(postgres_connection)
            pass
        else:
            raise ValueError(f"Unsupported database engine: {self.db_engine}")
        
    async def initialize_all(self):
        """Initializes all repositories based on the active DB engine."""
        print(f"Initializing {self.db_engine} database components...")
        await self.user_repo.initialize()
        await self.player_repo.initialize()
        await self.lobby_repo.initialize()

db = DatabaseFactory()