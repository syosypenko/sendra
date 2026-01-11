from motor.motor_asyncio import AsyncIOMotorClient
from src.config import settings

class Database:
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect_db(cls):
        cls.client = AsyncIOMotorClient(settings.mongodb_uri)
        print("Connected to MongoDB")
    
    @classmethod
    async def close_db(cls):
        cls.client.close()
        print("Closed MongoDB connection")
    
    @classmethod
    def get_db(cls):
        return cls.client.sendra_emails

db = Database()
