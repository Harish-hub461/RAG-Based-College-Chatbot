from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

import certifi

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongodb = MongoDB()

import certifi

async def connect_to_mongo():
    """Connect to MongoDB Atlas on startup."""
    try:
        mongodb.client = AsyncIOMotorClient(
            settings.DATABASE_URL,
            tlsAllowInvalidCertificates=True
        )
        mongodb.db = mongodb.client.get_default_database()
        print(f"[MongoDB] Connected to database: {mongodb.db.name}")
    except Exception as e:
        print(f"[MongoDB] Connection error: {e}")
        raise e


async def close_mongo_connection():
    """Close MongoDB connection on shutdown."""
    if mongodb.client:
        mongodb.client.close()
        print("[MongoDB] Connection closed.")

def get_db():
    """Return the MongoDB database instance."""
    return mongodb.db
