from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pymongo import DESCENDING, ASCENDING
from bson import ObjectId

from .base import BaseRepository
from ..models.video import Video, VideoCategory, VideoStatus
from ..core.cache import cache_result


class VideoRepository(BaseRepository[Video]):
    """Enterprise-grade video repository with advanced querying and caching"""
    
    def __init__(self):
        super().__init__(Video, "videos")
    
    @cache_result("video_by_id", expire=timedelta(minutes=30))
    async def get_by_id(self, document_id: str) -> Optional[Video]:
        """Get video by ID with caching"""
        return await super().get_by_id(document_id)
    
    async def get_by_channel(
        self,
        channel_id: str,
        status: VideoStatus = VideoStatus.PUBLISHED,
        limit: int = 50,
        offset: int = 0
    ) -> List[Video]:
        """Get videos by channel"""
        filter_dict = {
            "channel_id": ObjectId(channel_id),
            "status": status
        }
        
        return await self.find_many(
            filter_dict=filter_dict,
            sort_by="created_at",
            sort_order=DESCENDING,
            limit=limit,
            offset=offset
        )
    
    @cache_result("videos_by_category", expire=timedelta(minutes=15))
    async def get_by_category(
        self,
        category: VideoCategory,
        status: VideoStatus = VideoStatus.PUBLISHED,
        limit: int = 50,
        offset: int = 0
    ) -> List[Video]:
        """Get videos by category with caching"""
        filter_dict = {
            "category": category,
            "status": status
        }
        
        return await self.find_many(
            filter_dict=filter_dict,
            sort_by="created_at",
            sort_order=DESCENDING,
            limit=limit,
            offset=offset
        )
    
    @cache_result("trending_videos", expire=timedelta(minutes=10))
    async def get_trending(
        self,
        category: Optional[VideoCategory] = None,
        hours_back: int = 72,
        limit: int = 50
    ) -> List[Video]:
        """Get trending videos based on engagement and recency"""
        collection = await self.get_collection()
        
        # Build match stage
        match_stage = {
            "status": VideoStatus.PUBLISHED,
            "created_at": {"$gte": datetime.utcnow() - timedelta(hours=hours_back)}
        }
        
        if category:
            match_stage["category"] = category
        
        # Aggregation pipeline for trending calculation
        pipeline = [
            {"$match": match_stage},
            {
                "$addFields": {
                    "engagement_score": {
                        "$add": [
                            {"$multiply": ["$metrics.likes", 1]},
                            {"$multiply": ["$metrics.comments_count", 2]},
                            {"$multiply": ["$metrics.shares", 3]},
                            {"$multiply": ["$metrics.views", 0.1]}
                        ]
                    },
                    "age_hours": {
                        "$divide": [
                            {"$subtract": ["$$NOW", "$created_at"]},
                            3600000  # Convert to hours
                        ]
                    }
                }
            },
            {
                "$addFields": {
                    "age_penalty": {
                        "$max": [
                            0.1,
                            {"$divide": [1, {"$add": [1, {"$divide": ["$age_hours", 24]}]}]}
                        ]
                    }
                }
            },
            {
                "$addFields": {
                    "final_trending_score": {"$multiply": ["$engagement_score", "$age_penalty"]}
                }
            },
            {"$sort": {"final_trending_score": -1}},
            {"$limit": limit}
        ]
        
        results = await self.aggregate(pipeline)
        return [Video(**doc) for doc in results]
    
    async def search_videos(
        self,
        query: str,
        category: Optional[VideoCategory] = None,
        sort_by: str = "relevance",
        limit: int = 50,
        offset: int = 0
    ) -> List[Video]:
        """Advanced video search with relevance scoring"""
        collection = await self.get_collection()
        
        # Build search pipeline
        match_stage = {
            "$text": {"$search": query},
            "status": VideoStatus.PUBLISHED
        }
        
        if category:
            match_stage["category"] = category
        
        # Sort options
        sort_options = {
            "relevance": [("score", {"$meta": "textScore"})],
            "date": [("created_at", DESCENDING)],
            "views": [("metrics.views", DESCENDING)],
            "likes": [("metrics.likes", DESCENDING)]
        }
        
        sort_stage = sort_options.get(sort_by, sort_options["relevance"])
        
        # Execute search with aggregation for better performance
        pipeline = [
            {"$match": match_stage},
            {"$addFields": {"score": {"$meta": "textScore"}}},
            {"$sort": dict(sort_stage)},
            {"$skip": offset},
            {"$limit": limit}
        ]
        
        results = await self.aggregate(pipeline)
        return [Video(**doc) for doc in results]
    
    async def get_recommended_for_video(
        self,
        video_id: str,
        limit: int = 20
    ) -> List[Video]:
        """Get recommended videos based on content similarity"""
        current_video = await self.get_by_id(video_id)
        if not current_video:
            return []
        
        collection = await self.get_collection()
        
        # Content-based recommendation pipeline
        pipeline = [
            {
                "$match": {
                    "_id": {"$ne": ObjectId(video_id)},
                    "status": VideoStatus.PUBLISHED,
                    "$or": [
                        {"category": current_video.category},
                        {"tags": {"$in": current_video.tags}},
                        {"channel_id": current_video.channel_id}
                    ]
                }
            },
            {
                "$addFields": {
                    "similarity_score": {
                        "$add": [
                            # Category match bonus
                            {"$cond": [{"$eq": ["$category", current_video.category]}, 3, 0]},
                            # Channel match bonus (if different video from same channel)
                            {"$cond": [{"$eq": ["$channel_id", current_video.channel_id]}, 2, 0]},
                            # Tag overlap bonus
                            {"$size": {"$setIntersection": ["$tags", current_video.tags]}}
                        ]
                    }
                }
            },
            {"$sort": {"similarity_score": -1, "metrics.views": -1}},
            {"$limit": limit}
        ]
        
        results = await self.aggregate(pipeline)
        return [Video(**doc) for doc in results]
    
    async def get_popular_by_timeframe(
        self,
        timeframe_hours: int = 24,
        category: Optional[VideoCategory] = None,
        limit: int = 50
    ) -> List[Video]:
        """Get popular videos within a specific timeframe"""
        since_date = datetime.utcnow() - timedelta(hours=timeframe_hours)
        
        filter_dict = {
            "status": VideoStatus.PUBLISHED,
            "created_at": {"$gte": since_date}
        }
        
        if category:
            filter_dict["category"] = category
        
        return await self.find_many(
            filter_dict=filter_dict,
            sort_by="metrics.views",
            sort_order=DESCENDING,
            limit=limit
        )
    
    async def update_video_metrics(
        self,
        video_id: str,
        metrics_update: Dict[str, Any]
    ) -> Optional[Video]:
        """Update video metrics with automatic trending score calculation"""
        video = await self.get_by_id(video_id)
        if not video:
            return None
        
        # Update metrics
        for key, value in metrics_update.items():
            if hasattr(video.metrics, key):
                if key in ['views', 'likes', 'dislikes', 'comments_count', 'shares']:
                    # For counters, we can either set or increment
                    if isinstance(value, dict) and '$inc' in value:
                        current_value = getattr(video.metrics, key)
                        setattr(video.metrics, key, current_value + value['$inc'])
                    else:
                        setattr(video.metrics, key, value)
                else:
                    setattr(video.metrics, key, value)
        
        # Recalculate engagement rate and trending score
        video.metrics.engagement_rate = video.metrics.calculate_engagement_rate()
        video.update_trending_score()
        
        # Update in database
        update_data = {
            "metrics": video.metrics.dict(),
            "trending_score": video.trending_score
        }
        
        return await self.update_by_id(video_id, update_data)
    
    async def get_channel_stats(self, channel_id: str) -> Dict[str, Any]:
        """Get aggregated statistics for a channel"""
        collection = await self.get_collection()
        
        pipeline = [
            {
                "$match": {
                    "channel_id": ObjectId(channel_id),
                    "status": VideoStatus.PUBLISHED
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_videos": {"$sum": 1},
                    "total_views": {"$sum": "$metrics.views"},
                    "total_likes": {"$sum": "$metrics.likes"},
                    "total_comments": {"$sum": "$metrics.comments_count"},
                    "avg_duration": {"$avg": "$duration_seconds"},
                    "latest_upload": {"$max": "$created_at"},
                    "oldest_upload": {"$min": "$created_at"}
                }
            }
        ]
        
        results = await self.aggregate(pipeline)
        return results[0] if results else {}


# Global repository instance
video_repository = VideoRepository()