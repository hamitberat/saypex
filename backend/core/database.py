import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import asyncio
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Enterprise-grade database manager with connection pooling and replica sets"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._connection_string = os.environ.get('MONGO_URL')
        self._database_name = os.environ.get('DB_NAME', 'youtube_clone')
        
    async def connect(self):
        """Connect to MongoDB with enterprise settings"""
        try:
            self.client = AsyncIOMotorClient(
                self._connection_string,
                maxPoolSize=50,  # Maximum connections in pool
                minPoolSize=10,  # Minimum connections to maintain
                maxIdleTimeMS=30000,  # Close connections after 30s idle
                serverSelectionTimeoutMS=5000,  # 5s timeout for server selection
                connectTimeoutMS=10000,  # 10s connection timeout
                socketTimeoutMS=20000,  # 20s socket timeout
                heartbeatFrequencyMS=10000,  # Heartbeat every 10s
                retryReads=True,  # Retry read operations
                retryWrites=True,  # Retry write operations
                w='majority',  # Write concern for consistency
                readPreference='primaryPreferred'  # Read from primary when available
                # Removed readConcern as it's not supported in this format
            )
            
            # Test connection
            await self.client.admin.command('ping')
            self.database = self.client[self._database_name]
            
            # Create indexes for optimal performance
            await self._create_indexes()
            
            logger.info(f"Connected to MongoDB database: {self._database_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Gracefully disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Video indexes
            videos_collection = self.database.videos
            await videos_collection.create_index([("channel_id", 1)])
            await videos_collection.create_index([("category", 1), ("created_at", -1)])
            await videos_collection.create_index([("status", 1), ("created_at", -1)])
            await videos_collection.create_index([("trending_score", -1), ("created_at", -1)])
            await videos_collection.create_index([
                ("title", "text"), 
                ("description", "text"), 
                ("tags", "text"),
                ("search_keywords", "text")
            ], name="video_search_index")
            
            # User indexes
            users_collection = self.database.users
            await users_collection.create_index([("email", 1)], unique=True)
            await users_collection.create_index([("username", 1)], unique=True)
            await users_collection.create_index([("channel_id", 1)])
            await users_collection.create_index([("role", 1), ("status", 1)])
            
            # Comment indexes
            comments_collection = self.database.comments
            await comments_collection.create_index([("video_id", 1), ("created_at", -1)])
            await comments_collection.create_index([("parent_id", 1), ("created_at", 1)])
            await comments_collection.create_index([("thread_id", 1), ("depth", 1)])
            await comments_collection.create_index([("author_id", 1), ("created_at", -1)])
            
            # User interactions indexes
            await self.database.user_video_interactions.create_index([
                ("user_id", 1), ("video_id", 1)
            ], unique=True)
            await self.database.user_video_interactions.create_index([("video_id", 1)])
            await self.database.user_video_interactions.create_index([("user_id", 1), ("interaction_type", 1)])
            
            # Subscription indexes
            await self.database.subscriptions.create_index([
                ("subscriber_id", 1), ("channel_id", 1)
            ], unique=True)
            await self.database.subscriptions.create_index([("channel_id", 1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database indexes: {e}")
    
    @asynccontextmanager
    async def get_session(self):
        """Get a database session for transactions"""
        async with await self.client.start_session() as session:
            yield session
    
    async def execute_transaction(self, operations, session=None):
        """Execute multiple operations in a transaction"""
        if session is None:
            async with await self.client.start_session() as session:
                return await self._run_transaction(operations, session)
        else:
            return await self._run_transaction(operations, session)
    
    async def _run_transaction(self, operations, session):
        """Run transaction with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with session.start_transaction():
                    results = []
                    for operation in operations:
                        result = await operation(session)
                        results.append(result)
                    return results
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Transaction attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff


# Global database manager instance
db_manager = DatabaseManager()


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if db_manager.database is None:
        await db_manager.connect()
    return db_manager.database


async def init_database():
    """Initialize database connection"""
    await db_manager.connect()


async def close_database():
    """Close database connection"""
    await db_manager.disconnect()