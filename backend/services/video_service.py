from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ..models.video import (
    Video, VideoResponse, VideoCreateRequest, VideoUpdateRequest, 
    VideoCategory, VideoStatus, VideoMetrics
)
from ..repositories.video_repository import video_repository
from ..repositories.user_repository import user_repository
from ..core.cache import get_cache
from ..services.recommendation_service import recommendation_service

logger = logging.getLogger(__name__)


class VideoService:
    """Enterprise video service with caching and business logic"""
    
    def __init__(self):
        self.video_repo = video_repository
        self.user_repo = user_repository
    
    async def create_video(
        self, 
        video_data: VideoCreateRequest,
        creator_id: str
    ) -> Optional[VideoResponse]:
        """Create a new video with validation"""
        try:
            # Validate creator permissions
            creator = await self.user_repo.get_by_id(creator_id)
            if not creator or not creator.can_upload_videos():
                logger.warning(f"User {creator_id} cannot upload videos")
                return None
            
            # Create video document
            video = Video(
                title=video_data.title,
                description=video_data.description,
                channel_id=creator.channel_id,
                channel_name=creator.channel_name,
                channel_avatar=creator.avatar_url,
                video_url=video_data.video_url,
                youtube_embed_url=video_data.youtube_embed_url,
                duration_seconds=video_data.duration_seconds,
                thumbnails=video_data.thumbnails,
                category=video_data.category,
                tags=video_data.tags,
                status=video_data.status,
                metrics=VideoMetrics()
            )
            
            # Save to database
            created_video = await self.video_repo.create(video)
            
            # Update creator stats
            await self.user_repo.update_user_stats(
                creator_id,
                {"videos_uploaded": {"$inc": 1}, "last_video_upload": datetime.utcnow()}
            )
            
            # Clear related caches
            cache = await get_cache()
            await cache.delete_pattern(f"videos_by_category:*")
            await cache.delete_pattern(f"trending_videos:*")
            
            logger.info(f"Video created: {created_video.id} by {creator_id}")
            return VideoResponse.from_video(created_video)
            
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            return None
    
    async def get_video(self, video_id: str, user_id: Optional[str] = None) -> Optional[VideoResponse]:
        """Get video by ID with view tracking"""
        try:
            video = await self.video_repo.get_by_id(video_id)
            if not video or video.status != VideoStatus.PUBLISHED:
                return None
            
            # Track view if user provided
            if user_id:
                await self._track_video_view(video_id, user_id)
            
            return VideoResponse.from_video(video)
            
        except Exception as e:
            logger.error(f"Error getting video {video_id}: {e}")
            return None
    
    async def update_video(
        self,
        video_id: str,
        update_data: VideoUpdateRequest,
        user_id: str
    ) -> Optional[VideoResponse]:
        """Update video with ownership validation"""
        try:
            video = await self.video_repo.get_by_id(video_id)
            if not video:
                return None
            
            # Check ownership
            user = await self.user_repo.get_by_id(user_id)
            if not user or str(video.channel_id) != str(user.channel_id):
                logger.warning(f"User {user_id} cannot edit video {video_id}")
                return None
            
            # Prepare update data
            update_dict = {}
            if update_data.title is not None:
                update_dict["title"] = update_data.title
            if update_data.description is not None:
                update_dict["description"] = update_data.description
            if update_data.category is not None:
                update_dict["category"] = update_data.category
            if update_data.tags is not None:
                update_dict["tags"] = update_data.tags
            if update_data.status is not None:
                update_dict["status"] = update_data.status
            
            # Update video
            updated_video = await self.video_repo.update_by_id(video_id, update_dict)
            if not updated_video:
                return None
            
            # Clear caches
            cache = await get_cache()
            await cache.delete(f"video_by_id:{video_id}")
            
            logger.info(f"Video updated: {video_id} by {user_id}")
            return VideoResponse.from_video(updated_video)
            
        except Exception as e:
            logger.error(f"Error updating video {video_id}: {e}")
            return None
    
    async def delete_video(self, video_id: str, user_id: str) -> bool:
        """Soft delete video with ownership validation"""
        try:
            video = await self.video_repo.get_by_id(video_id)
            if not video:
                return False
            
            # Check ownership
            user = await self.user_repo.get_by_id(user_id)
            if not user or str(video.channel_id) != str(user.channel_id):
                logger.warning(f"User {user_id} cannot delete video {video_id}")
                return False
            
            # Soft delete
            success = await self.video_repo.soft_delete_by_id(video_id, user_id)
            
            if success:
                # Update creator stats
                await self.user_repo.update_user_stats(
                    user_id,
                    {"videos_uploaded": {"$inc": -1}}
                )
                
                # Clear caches
                cache = await get_cache()
                await cache.delete(f"video_by_id:{video_id}")
                await cache.delete_pattern(f"videos_by_category:*")
                
                logger.info(f"Video deleted: {video_id} by {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting video {video_id}: {e}")
            return False
    
    async def get_home_videos(
        self,
        category: Optional[VideoCategory] = None,
        limit: int = 50,
        offset: int = 0,
        user_id: Optional[str] = None
    ) -> List[VideoResponse]:
        """Get videos for home page with personalization"""
        try:
            if category:
                videos = await self.video_repo.get_by_category(category, limit=limit, offset=offset)
            else:
                # Get personalized recommendations if user is logged in
                if user_id:
                    videos = await recommendation_service.get_personalized_videos(
                        user_id, limit=limit, offset=offset
                    )
                else:
                    # Get trending videos for anonymous users
                    videos = await self.video_repo.get_trending(limit=limit)
            
            return [VideoResponse.from_video(video) for video in videos]
            
        except Exception as e:
            logger.error(f"Error getting home videos: {e}")
            return []
    
    async def get_trending_videos(
        self,
        category: Optional[VideoCategory] = None,
        limit: int = 50
    ) -> List[VideoResponse]:
        """Get trending videos"""
        try:
            videos = await self.video_repo.get_trending(category=category, limit=limit)
            return [VideoResponse.from_video(video) for video in videos]
            
        except Exception as e:
            logger.error(f"Error getting trending videos: {e}")
            return []
    
    async def search_videos(
        self,
        query: str,
        category: Optional[VideoCategory] = None,
        sort_by: str = "relevance",
        limit: int = 50,
        offset: int = 0
    ) -> List[VideoResponse]:
        """Search videos with advanced filtering"""
        try:
            videos = await self.video_repo.search_videos(
                query=query,
                category=category,
                sort_by=sort_by,
                limit=limit,
                offset=offset
            )
            
            return [VideoResponse.from_video(video) for video in videos]
            
        except Exception as e:
            logger.error(f"Error searching videos: {e}")
            return []
    
    async def get_recommended_videos(
        self, 
        video_id: str, 
        limit: int = 20
    ) -> List[VideoResponse]:
        """Get recommended videos for video player"""
        try:
            videos = await self.video_repo.get_recommended_for_video(video_id, limit)
            return [VideoResponse.from_video(video) for video in videos]
            
        except Exception as e:
            logger.error(f"Error getting recommended videos: {e}")
            return []
    
    async def get_channel_videos(
        self,
        channel_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[VideoResponse]:
        """Get videos from a specific channel"""
        try:
            videos = await self.video_repo.get_by_channel(
                channel_id, limit=limit, offset=offset
            )
            return [VideoResponse.from_video(video) for video in videos]
            
        except Exception as e:
            logger.error(f"Error getting channel videos: {e}")
            return []
    
    async def like_video(self, video_id: str, user_id: str) -> bool:
        """Like a video"""
        try:
            # Check if already liked
            if await self._has_user_interaction(video_id, user_id, "like"):
                return False
            
            # Remove dislike if exists
            await self._remove_user_interaction(video_id, user_id, "dislike")
            
            # Add like
            await self._add_user_interaction(video_id, user_id, "like")
            
            # Update video metrics
            await self.video_repo.update_video_metrics(
                video_id, {"likes": {"$inc": 1}}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error liking video {video_id}: {e}")
            return False
    
    async def dislike_video(self, video_id: str, user_id: str) -> bool:
        """Dislike a video"""
        try:
            # Check if already disliked
            if await self._has_user_interaction(video_id, user_id, "dislike"):
                return False
            
            # Remove like if exists
            await self._remove_user_interaction(video_id, user_id, "like")
            
            # Add dislike
            await self._add_user_interaction(video_id, user_id, "dislike")
            
            # Update video metrics
            await self.video_repo.update_video_metrics(
                video_id, {"dislikes": {"$inc": 1}}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error disliking video {video_id}: {e}")
            return False
    
    async def remove_video_reaction(self, video_id: str, user_id: str) -> bool:
        """Remove like or dislike from video"""
        try:
            # Check current interaction
            like_exists = await self._has_user_interaction(video_id, user_id, "like")
            dislike_exists = await self._has_user_interaction(video_id, user_id, "dislike")
            
            if like_exists:
                await self._remove_user_interaction(video_id, user_id, "like")
                await self.video_repo.update_video_metrics(
                    video_id, {"likes": {"$inc": -1}}
                )
                return True
            elif dislike_exists:
                await self._remove_user_interaction(video_id, user_id, "dislike")
                await self.video_repo.update_video_metrics(
                    video_id, {"dislikes": {"$inc": -1}}
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing video reaction {video_id}: {e}")
            return False
    
    async def _track_video_view(self, video_id: str, user_id: str):
        """Track video view with duplicate prevention"""
        try:
            # Check if user viewed this video recently (last hour)
            cache = await get_cache()
            cache_key = f"view:{user_id}:{video_id}"
            
            if await cache.exists(cache_key):
                return  # Already counted recently
            
            # Set cache to prevent duplicate views for 1 hour
            await cache.set(cache_key, True, expire=3600)
            
            # Update video metrics
            await self.video_repo.update_video_metrics(
                video_id, {"views": {"$inc": 1}}
            )
            
            # Update user stats
            await self.user_repo.update_user_stats(
                user_id, {"videos_watched": {"$inc": 1}}
            )
            
            # Store view for recommendation engine
            await self._record_user_interaction(video_id, user_id, "view")
            
        except Exception as e:
            logger.error(f"Error tracking video view: {e}")
    
    async def _has_user_interaction(
        self, 
        video_id: str, 
        user_id: str, 
        interaction_type: str
    ) -> bool:
        """Check if user has specific interaction with video"""
        try:
            db = await self.video_repo.get_collection()
            interactions = db.database.user_video_interactions
            
            result = await interactions.find_one({
                "user_id": user_id,
                "video_id": video_id,
                "interaction_type": interaction_type
            })
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Error checking user interaction: {e}")
            return False
    
    async def _add_user_interaction(
        self, 
        video_id: str, 
        user_id: str, 
        interaction_type: str
    ):
        """Add user interaction with video"""
        try:
            db = await self.video_repo.get_collection()
            interactions = db.database.user_video_interactions
            
            await interactions.insert_one({
                "user_id": user_id,
                "video_id": video_id,
                "interaction_type": interaction_type,
                "created_at": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Error adding user interaction: {e}")
    
    async def _remove_user_interaction(
        self, 
        video_id: str, 
        user_id: str, 
        interaction_type: str
    ):
        """Remove user interaction with video"""
        try:
            db = await self.video_repo.get_collection()
            interactions = db.database.user_video_interactions
            
            await interactions.delete_one({
                "user_id": user_id,
                "video_id": video_id,
                "interaction_type": interaction_type
            })
            
        except Exception as e:
            logger.error(f"Error removing user interaction: {e}")
    
    async def _record_user_interaction(
        self, 
        video_id: str, 
        user_id: str, 
        interaction_type: str
    ):
        """Record user interaction for ML recommendations"""
        try:
            db = await self.video_repo.get_collection()
            interactions = db.database.user_video_interactions
            
            # Use upsert to avoid duplicates
            await interactions.update_one(
                {
                    "user_id": user_id,
                    "video_id": video_id,
                    "interaction_type": interaction_type
                },
                {
                    "$set": {
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error recording user interaction: {e}")


# Global service instance
video_service = VideoService()