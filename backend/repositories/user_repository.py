from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pymongo import DESCENDING
from bson import ObjectId

from .base import BaseRepository
from ..models.user import User, UserRole, UserStatus
from ..core.cache import cache_result


class UserRepository(BaseRepository[User]):
    """Enterprise-grade user repository with authentication and social features"""
    
    def __init__(self):
        super().__init__(User, "users")
    
    @cache_result("user_by_id", expire=timedelta(minutes=15))
    async def get_by_id(self, document_id: str) -> Optional[User]:
        """Get user by ID with caching"""
        return await super().get_by_id(document_id)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.get_by_field("email", email.lower())
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return await self.get_by_field("username", username.lower())
    
    async def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.VIEWER
    ) -> User:
        """Create a new user with validation"""
        user = User(
            username=username.lower(),
            email=email.lower(),
            password_hash=password_hash,
            full_name=full_name,
            role=role
        )
        
        return await self.create(user)
    
    async def update_password(self, user_id: str, new_password_hash: str) -> bool:
        """Update user password"""
        update_data = {
            "password_hash": new_password_hash,
            "password_reset_token": None,
            "password_reset_expires": None
        }
        
        result = await self.update_by_id(user_id, update_data)
        return result is not None
    
    async def verify_email(self, user_id: str) -> bool:
        """Verify user email"""
        update_data = {
            "is_email_verified": True,
            "email_verification_token": None
        }
        
        result = await self.update_by_id(user_id, update_data)
        return result is not None
    
    async def set_password_reset_token(
        self,
        user_id: str,
        reset_token: str,
        expires_at: datetime
    ) -> bool:
        """Set password reset token"""
        update_data = {
            "password_reset_token": reset_token,
            "password_reset_expires": expires_at
        }
        
        result = await self.update_by_id(user_id, update_data)
        return result is not None
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        update_data = {"last_login": datetime.utcnow()}
        result = await self.update_by_id(user_id, update_data)
        return result is not None
    
    async def create_channel(
        self,
        user_id: str,
        channel_name: str,
        channel_description: Optional[str] = None
    ) -> Optional[User]:
        """Create a channel for the user"""
        # Generate channel ID
        channel_id = ObjectId()
        
        update_data = {
            "channel_id": channel_id,
            "channel_name": channel_name,
            "channel_description": channel_description,
            "role": UserRole.CREATOR
        }
        
        return await self.update_by_id(user_id, update_data)
    
    async def subscribe_to_channel(
        self,
        subscriber_id: str,
        channel_id: str
    ) -> bool:
        """Subscribe user to a channel"""
        collection = await self.get_collection()
        
        # Add channel to user's subscriptions
        result = await collection.update_one(
            {"_id": ObjectId(subscriber_id)},
            {"$addToSet": {"subscribed_channels": ObjectId(channel_id)}}
        )
        
        if result.modified_count > 0:
            # Update subscriber count for the channel owner
            await collection.update_one(
                {"channel_id": ObjectId(channel_id)},
                {"$inc": {"stats.subscribers_count": 1}}
            )
        
        return result.modified_count > 0
    
    async def unsubscribe_from_channel(
        self,
        subscriber_id: str,
        channel_id: str
    ) -> bool:
        """Unsubscribe user from a channel"""
        collection = await self.get_collection()
        
        # Remove channel from user's subscriptions
        result = await collection.update_one(
            {"_id": ObjectId(subscriber_id)},
            {"$pull": {"subscribed_channels": ObjectId(channel_id)}}
        )
        
        if result.modified_count > 0:
            # Update subscriber count for the channel owner
            await collection.update_one(
                {"channel_id": ObjectId(channel_id)},
                {"$inc": {"stats.subscribers_count": -1}}
            )
        
        return result.modified_count > 0
    
    async def get_subscriptions(self, user_id: str) -> List[User]:
        """Get all channels the user is subscribed to"""
        user = await self.get_by_id(user_id)
        if not user or not user.subscribed_channels:
            return []
        
        collection = await self.get_collection()
        cursor = collection.find({
            "channel_id": {"$in": user.subscribed_channels}
        })
        
        documents = await cursor.to_list(length=None)
        return [User(**doc) for doc in documents]
    
    async def get_subscribers(self, channel_id: str, limit: int = 50) -> List[User]:
        """Get subscribers of a channel"""
        collection = await self.get_collection()
        cursor = collection.find({
            "subscribed_channels": ObjectId(channel_id)
        }).limit(limit)
        
        documents = await cursor.to_list(length=limit)
        return [User(**doc) for doc in documents]
    
    async def is_subscribed(self, subscriber_id: str, channel_id: str) -> bool:
        """Check if user is subscribed to a channel"""
        collection = await self.get_collection()
        result = await collection.find_one({
            "_id": ObjectId(subscriber_id),
            "subscribed_channels": ObjectId(channel_id)
        })
        return result is not None
    
    async def update_user_stats(
        self,
        user_id: str,
        stats_update: Dict[str, Any]
    ) -> Optional[User]:
        """Update user statistics"""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        # Update stats
        for key, value in stats_update.items():
            if hasattr(user.stats, key):
                if isinstance(value, dict) and '$inc' in value:
                    current_value = getattr(user.stats, key)
                    setattr(user.stats, key, current_value + value['$inc'])
                else:
                    setattr(user.stats, key, value)
        
        user.stats.last_active = datetime.utcnow()
        
        # Update in database
        update_data = {"stats": user.stats.dict()}
        return await self.update_by_id(user_id, update_data)
    
    async def search_users(
        self,
        query: str,
        limit: int = 20
    ) -> List[User]:
        """Search users by username or channel name"""
        collection = await self.get_collection()
        
        # Create search filter
        search_filter = {
            "$or": [
                {"username": {"$regex": query, "$options": "i"}},
                {"channel_name": {"$regex": query, "$options": "i"}},
                {"full_name": {"$regex": query, "$options": "i"}}
            ],
            "status": UserStatus.ACTIVE
        }
        
        cursor = collection.find(search_filter).limit(limit)
        documents = await cursor.to_list(length=limit)
        return [User(**doc) for doc in documents]
    
    async def get_top_creators(self, limit: int = 50) -> List[User]:
        """Get top creators by subscriber count"""
        filter_dict = {
            "role": {"$in": [UserRole.CREATOR, UserRole.ADMIN]},
            "status": UserStatus.ACTIVE,
            "channel_id": {"$ne": None}
        }
        
        return await self.find_many(
            filter_dict=filter_dict,
            sort_by="stats.subscribers_count",
            sort_order=DESCENDING,
            limit=limit
        )
    
    async def get_user_activity_summary(self, user_id: str) -> Dict[str, Any]:
        """Get user activity summary for analytics"""
        collection = await self.get_collection()
        
        pipeline = [
            {"$match": {"_id": ObjectId(user_id)}},
            {
                "$project": {
                    "username": 1,
                    "role": 1,
                    "created_at": 1,
                    "last_login": 1,
                    "stats": 1,
                    "subscriptions_count": {"$size": "$subscribed_channels"},
                    "account_age_days": {
                        "$divide": [
                            {"$subtract": ["$$NOW", "$created_at"]},
                            86400000  # Convert to days
                        ]
                    }
                }
            }
        ]
        
        results = await self.aggregate(pipeline)
        return results[0] if results else {}


# Global repository instance
user_repository = UserRepository()