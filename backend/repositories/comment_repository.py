from typing import List, Optional, Dict, Any
from datetime import datetime
from pymongo import DESCENDING, ASCENDING
from bson import ObjectId

from .base import BaseRepository
from ..models.comment import Comment, CommentStatus
from ..core.cache import cache_result


class CommentRepository(BaseRepository[Comment]):
    """Enterprise-grade comment repository with threading and moderation"""
    
    def __init__(self):
        super().__init__(Comment, "comments")
    
    async def create_comment(
        self,
        content: str,
        video_id: str,
        author_id: str,
        author_username: str,
        author_avatar: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> Comment:
        """Create a new comment with proper threading"""
        # Determine thread ID and depth
        thread_id = ObjectId(parent_id) if parent_id else None
        depth = 0
        
        if parent_id:
            parent_comment = await self.get_by_id(parent_id)
            if parent_comment:
                thread_id = parent_comment.thread_id
                depth = parent_comment.depth + 1
                
                # Update parent's reply count
                await self.update_comment_metrics(
                    parent_id,
                    {"replies_count": {"$inc": 1}}
                )
        
        comment = Comment(
            content=content,
            video_id=ObjectId(video_id),
            author_id=ObjectId(author_id),
            author_username=author_username,
            author_avatar=author_avatar,
            parent_id=ObjectId(parent_id) if parent_id else None,
            thread_id=thread_id or ObjectId(),  # Use new ObjectId if no parent
            depth=depth
        )
        
        # If this is a root comment, set thread_id to its own ID after creation
        created_comment = await self.create(comment)
        if not parent_id:
            await self.update_by_id(
                str(created_comment.id),
                {"thread_id": created_comment.id}
            )
            created_comment.thread_id = created_comment.id
        
        return created_comment
    
    @cache_result("video_comments", expire=300)  # 5 minutes
    async def get_video_comments(
        self,
        video_id: str,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "created_at"
    ) -> List[Comment]:
        """Get top-level comments for a video"""
        filter_dict = {
            "video_id": ObjectId(video_id),
            "parent_id": None,  # Only root comments
            "status": CommentStatus.ACTIVE
        }
        
        sort_order = DESCENDING if sort_by == "created_at" else ASCENDING
        
        return await self.find_many(
            filter_dict=filter_dict,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )
    
    async def get_comment_replies(
        self,
        parent_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Comment]:
        """Get replies to a specific comment"""
        filter_dict = {
            "parent_id": ObjectId(parent_id),
            "status": CommentStatus.ACTIVE
        }
        
        return await self.find_many(
            filter_dict=filter_dict,
            sort_by="created_at",
            sort_order=ASCENDING,
            limit=limit,
            offset=offset
        )
    
    async def get_comment_thread(
        self,
        thread_id: str,
        limit: int = 100
    ) -> List[Comment]:
        """Get entire comment thread"""
        filter_dict = {
            "thread_id": ObjectId(thread_id),
            "status": CommentStatus.ACTIVE
        }
        
        return await self.find_many(
            filter_dict=filter_dict,
            sort_by="created_at",
            sort_order=ASCENDING,
            limit=limit
        )
    
    async def get_user_comments(
        self,
        author_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Comment]:
        """Get comments by a specific user"""
        filter_dict = {
            "author_id": ObjectId(author_id),
            "status": CommentStatus.ACTIVE
        }
        
        return await self.find_many(
            filter_dict=filter_dict,
            sort_by="created_at",
            sort_order=DESCENDING,
            limit=limit,
            offset=offset
        )
    
    async def update_comment_metrics(
        self,
        comment_id: str,
        metrics_update: Dict[str, Any]
    ) -> Optional[Comment]:
        """Update comment metrics"""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return None
        
        # Update metrics
        for key, value in metrics_update.items():
            if hasattr(comment.metrics, key):
                if isinstance(value, dict) and '$inc' in value:
                    current_value = getattr(comment.metrics, key)
                    setattr(comment.metrics, key, current_value + value['$inc'])
                else:
                    setattr(comment.metrics, key, value)
        
        # Update in database
        update_data = {"metrics": comment.metrics.dict()}
        return await self.update_by_id(comment_id, update_data)
    
    async def like_comment(self, comment_id: str, user_id: str) -> bool:
        """Like a comment (with duplicate prevention)"""
        # Check if user already liked this comment
        collection = await self.get_collection()
        interactions_collection = collection.database.comment_interactions
        
        existing_like = await interactions_collection.find_one({
            "user_id": ObjectId(user_id),
            "comment_id": ObjectId(comment_id),
            "interaction_type": "like"
        })
        
        if existing_like:
            return False  # Already liked
        
        # Add like interaction
        await interactions_collection.insert_one({
            "user_id": ObjectId(user_id),
            "comment_id": ObjectId(comment_id),
            "interaction_type": "like",
            "created_at": datetime.utcnow()
        })
        
        # Update comment metrics
        await self.update_comment_metrics(comment_id, {"likes": {"$inc": 1}})
        return True
    
    async def unlike_comment(self, comment_id: str, user_id: str) -> bool:
        """Remove like from a comment"""
        collection = await self.get_collection()
        interactions_collection = collection.database.comment_interactions
        
        # Remove like interaction
        result = await interactions_collection.delete_one({
            "user_id": ObjectId(user_id),
            "comment_id": ObjectId(comment_id),
            "interaction_type": "like"
        })
        
        if result.deleted_count > 0:
            # Update comment metrics
            await self.update_comment_metrics(comment_id, {"likes": {"$inc": -1}})
            return True
        
        return False
    
    async def pin_comment(self, comment_id: str) -> bool:
        """Pin a comment (creator/moderator action)"""
        update_data = {"is_pinned": True}
        result = await self.update_by_id(comment_id, update_data)
        return result is not None
    
    async def unpin_comment(self, comment_id: str) -> bool:
        """Unpin a comment"""
        update_data = {"is_pinned": False}
        result = await self.update_by_id(comment_id, update_data)
        return result is not None
    
    async def heart_comment(self, comment_id: str) -> bool:
        """Heart a comment (creator action)"""
        update_data = {"is_creator_hearted": True}
        result = await self.update_by_id(comment_id, update_data)
        return result is not None
    
    async def unheart_comment(self, comment_id: str) -> bool:
        """Remove heart from comment"""
        update_data = {"is_creator_hearted": False}
        result = await self.update_by_id(comment_id, update_data)
        return result is not None
    
    async def moderate_comment(
        self,
        comment_id: str,
        action: str,
        moderator_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """Moderate a comment (hide, delete, approve)"""
        status_map = {
            "hide": CommentStatus.HIDDEN,
            "delete": CommentStatus.DELETED,
            "approve": CommentStatus.ACTIVE
        }
        
        if action not in status_map:
            return False
        
        update_data = {
            "status": status_map[action],
            "moderated_by": ObjectId(moderator_id),
            "moderated_at": datetime.utcnow(),
            "moderation_reason": reason
        }
        
        result = await self.update_by_id(comment_id, update_data)
        return result is not None
    
    async def flag_comment(self, comment_id: str, user_id: str) -> bool:
        """Flag a comment for review"""
        collection = await self.get_collection()
        
        result = await collection.update_one(
            {"_id": ObjectId(comment_id)},
            {
                "$addToSet": {"flagged_by": ObjectId(user_id)},
                "$inc": {"metrics.reports_count": 1}
            }
        )
        
        return result.modified_count > 0
    
    async def get_video_comment_stats(self, video_id: str) -> Dict[str, Any]:
        """Get comment statistics for a video"""
        collection = await self.get_collection()
        
        pipeline = [
            {
                "$match": {
                    "video_id": ObjectId(video_id),
                    "status": CommentStatus.ACTIVE
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_comments": {"$sum": 1},
                    "total_likes": {"$sum": "$metrics.likes"},
                    "avg_depth": {"$avg": "$depth"},
                    "latest_comment": {"$max": "$created_at"},
                    "root_comments": {
                        "$sum": {"$cond": [{"$eq": ["$parent_id", None]}, 1, 0]}
                    },
                    "reply_comments": {
                        "$sum": {"$cond": [{"$ne": ["$parent_id", None]}, 1, 0]}
                    }
                }
            }
        ]
        
        results = await self.aggregate(pipeline)
        return results[0] if results else {}
    
    async def get_most_liked_comments(
        self,
        video_id: str,
        limit: int = 10
    ) -> List[Comment]:
        """Get most liked comments for a video"""
        filter_dict = {
            "video_id": ObjectId(video_id),
            "status": CommentStatus.ACTIVE
        }
        
        return await self.find_many(
            filter_dict=filter_dict,
            sort_by="metrics.likes",
            sort_order=DESCENDING,
            limit=limit
        )


# Global repository instance
comment_repository = CommentRepository()