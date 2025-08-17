from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
import random
from collections import defaultdict, Counter
import math

from ..models.video import Video, VideoCategory
from ..repositories.video_repository import video_repository
from ..repositories.user_repository import user_repository
from ..core.cache import cache_result
from ..core.database import get_database

logger = logging.getLogger(__name__)


class RecommendationService:
    """Enterprise ML-powered recommendation service"""
    
    def __init__(self):
        self.video_repo = video_repository
        self.user_repo = user_repository
    
    @cache_result("personalized_videos", expire=timedelta(minutes=30))
    async def get_personalized_videos(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Video]:
        """Get personalized video recommendations using hybrid approach"""
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return await self._get_trending_fallback(limit, offset)
            
            # Get user interaction history
            user_interactions = await self._get_user_interactions(user_id)
            
            if not user_interactions:
                # New user - return popular videos from subscribed channels + trending
                return await self._get_new_user_recommendations(user_id, limit, offset)
            
            # Hybrid recommendation approach
            collaborative_videos = await self._collaborative_filtering(user_id, limit // 2)
            content_based_videos = await self._content_based_filtering(user_id, limit // 2)
            
            # Combine and deduplicate
            all_videos = collaborative_videos + content_based_videos
            seen_ids = set()
            unique_videos = []
            
            for video in all_videos:
                if str(video.id) not in seen_ids:
                    seen_ids.add(str(video.id))
                    unique_videos.append(video)
            
            # Apply offset and limit
            return unique_videos[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error getting personalized videos for user {user_id}: {e}")
            return await self._get_trending_fallback(limit, offset)
    
    async def _collaborative_filtering(self, user_id: str, limit: int) -> List[Video]:
        """Collaborative filtering based on similar users"""
        try:
            # Find users with similar viewing patterns
            similar_users = await self._find_similar_users(user_id, top_k=20)
            
            if not similar_users:
                return []
            
            # Get videos liked by similar users that current user hasn't seen
            video_scores = defaultdict(float)
            user_viewed_videos = await self._get_user_viewed_videos(user_id)
            
            for similar_user_id, similarity_score in similar_users:
                similar_user_videos = await self._get_user_liked_videos(similar_user_id)
                
                for video_id in similar_user_videos:
                    if video_id not in user_viewed_videos:
                        video_scores[video_id] += similarity_score
            
            # Sort by score and get top videos
            sorted_videos = sorted(video_scores.items(), key=lambda x: x[1], reverse=True)
            top_video_ids = [video_id for video_id, _ in sorted_videos[:limit]]
            
            # Fetch video objects
            videos = []
            for video_id in top_video_ids:
                video = await self.video_repo.get_by_id(video_id)
                if video:
                    videos.append(video)
            
            return videos[:limit]
            
        except Exception as e:
            logger.error(f"Error in collaborative filtering: {e}")
            return []
    
    async def _content_based_filtering(self, user_id: str, limit: int) -> List[Video]:
        """Content-based filtering based on user preferences"""
        try:
            # Analyze user's viewing history to determine preferences
            user_preferences = await self._analyze_user_preferences(user_id)
            
            if not user_preferences:
                return []
            
            # Find videos matching user preferences
            db = await get_database()
            videos_collection = db.videos
            
            # Build query based on preferences
            match_conditions = []
            
            # Category preferences
            if user_preferences.get('categories'):
                match_conditions.append({
                    "category": {"$in": list(user_preferences['categories'].keys())}
                })
            
            # Tag preferences
            if user_preferences.get('tags'):
                match_conditions.append({
                    "tags": {"$in": list(user_preferences['tags'].keys())}
                })
            
            # Channel preferences
            if user_preferences.get('channels'):
                match_conditions.append({
                    "channel_id": {"$in": list(user_preferences['channels'].keys())}
                })
            
            if not match_conditions:
                return []
            
            # Get user's viewed videos to exclude them
            user_viewed_videos = await self._get_user_viewed_videos(user_id)
            
            # Build aggregation pipeline
            pipeline = [
                {
                    "$match": {
                        "$and": [
                            {"$or": match_conditions},
                            {"status": "published"},
                            {"_id": {"$nin": user_viewed_videos}}
                        ]
                    }
                },
                {
                    "$addFields": {
                        "preference_score": {
                            "$add": [
                                # Category score
                                {"$cond": [
                                    {"$in": ["$category", list(user_preferences.get('categories', {}).keys())]},
                                    2.0, 0.0
                                ]},
                                # Tag score
                                {"$size": {"$setIntersection": ["$tags", list(user_preferences.get('tags', {}).keys())]}},
                                # Channel score
                                {"$cond": [
                                    {"$in": ["$channel_id", list(user_preferences.get('channels', {}).keys())]},
                                    3.0, 0.0
                                ]},
                                # Recent engagement bonus
                                {"$multiply": ["$metrics.likes", 0.01]},
                                {"$multiply": ["$metrics.views", 0.001]}
                            ]
                        }
                    }
                },
                {"$sort": {"preference_score": -1, "created_at": -1}},
                {"$limit": limit}
            ]
            
            results = await videos_collection.aggregate(pipeline).to_list(length=limit)
            return [Video(**doc) for doc in results]
            
        except Exception as e:
            logger.error(f"Error in content-based filtering: {e}")
            return []
    
    async def _find_similar_users(self, user_id: str, top_k: int = 20) -> List[Tuple[str, float]]:
        """Find users with similar viewing patterns using cosine similarity"""
        try:
            db = await get_database()
            interactions_collection = db.user_video_interactions
            
            # Get current user's interactions
            user_interactions = await interactions_collection.find({
                "user_id": user_id,
                "interaction_type": {"$in": ["like", "view"]}
            }).to_list(length=None)
            
            if not user_interactions:
                return []
            
            user_videos = set(interaction["video_id"] for interaction in user_interactions)
            
            # Find other users who interacted with similar videos
            pipeline = [
                {
                    "$match": {
                        "video_id": {"$in": list(user_videos)},
                        "user_id": {"$ne": user_id},
                        "interaction_type": {"$in": ["like", "view"]}
                    }
                },
                {
                    "$group": {
                        "_id": "$user_id",
                        "common_videos": {"$addToSet": "$video_id"},
                        "interaction_count": {"$sum": 1}
                    }
                },
                {
                    "$match": {
                        "interaction_count": {"$gte": 3}  # At least 3 common interactions
                    }
                },
                {"$limit": 100}  # Limit for performance
            ]
            
            similar_user_candidates = await interactions_collection.aggregate(pipeline).to_list(length=100)
            
            # Calculate cosine similarity
            similarities = []
            for candidate in similar_user_candidates:
                other_user_videos = set(candidate["common_videos"])
                
                # Calculate Jaccard similarity (simpler than cosine for binary data)
                intersection = len(user_videos & other_user_videos)
                union = len(user_videos | other_user_videos)
                
                if union > 0:
                    similarity = intersection / union
                    similarities.append((candidate["_id"], similarity))
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding similar users: {e}")
            return []
    
    async def _analyze_user_preferences(self, user_id: str) -> Dict[str, Dict[str, float]]:
        """Analyze user preferences based on interaction history"""
        try:
            db = await get_database()
            interactions_collection = db.user_video_interactions
            videos_collection = db.videos
            
            # Get user interactions with video details
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "interaction_type": {"$in": ["like", "view"]}
                    }
                },
                {
                    "$lookup": {
                        "from": "videos",
                        "localField": "video_id",
                        "foreignField": "_id",
                        "as": "video"
                    }
                },
                {"$unwind": "$video"},
                {
                    "$project": {
                        "interaction_type": 1,
                        "created_at": 1,
                        "video.category": 1,
                        "video.tags": 1,
                        "video.channel_id": 1
                    }
                }
            ]
            
            interactions = await interactions_collection.aggregate(pipeline).to_list(length=None)
            
            if not interactions:
                return {}
            
            preferences = {
                'categories': defaultdict(float),
                'tags': defaultdict(float),
                'channels': defaultdict(float)
            }
            
            # Weight recent interactions more heavily
            now = datetime.utcnow()
            
            for interaction in interactions:
                # Time decay factor (more recent = higher weight)
                days_old = (now - interaction['created_at']).days
                time_weight = math.exp(-days_old / 30)  # 30-day half-life
                
                # Interaction type weight
                interaction_weight = 2.0 if interaction['interaction_type'] == 'like' else 1.0
                
                total_weight = time_weight * interaction_weight
                
                # Update preferences
                video = interaction['video']
                preferences['categories'][video['category']] += total_weight
                
                for tag in video.get('tags', []):
                    preferences['tags'][tag] += total_weight
                
                preferences['channels'][str(video['channel_id'])] += total_weight
            
            # Convert to regular dict and normalize
            normalized_preferences = {}
            for pref_type, pref_dict in preferences.items():
                if pref_dict:
                    max_score = max(pref_dict.values())
                    normalized_preferences[pref_type] = {
                        k: v / max_score for k, v in pref_dict.items()
                    }
            
            return normalized_preferences
            
        except Exception as e:
            logger.error(f"Error analyzing user preferences: {e}")
            return {}
    
    async def _get_user_interactions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's interaction history"""
        try:
            db = await get_database()
            interactions_collection = db.user_video_interactions
            
            return await interactions_collection.find({
                "user_id": user_id
            }).to_list(length=None)
            
        except Exception as e:
            logger.error(f"Error getting user interactions: {e}")
            return []
    
    async def _get_user_viewed_videos(self, user_id: str) -> List[str]:
        """Get list of videos user has viewed"""
        try:
            db = await get_database()
            interactions_collection = db.user_video_interactions
            
            interactions = await interactions_collection.find({
                "user_id": user_id,
                "interaction_type": {"$in": ["view", "like", "dislike"]}
            }).to_list(length=None)
            
            return [interaction["video_id"] for interaction in interactions]
            
        except Exception as e:
            logger.error(f"Error getting user viewed videos: {e}")
            return []
    
    async def _get_user_liked_videos(self, user_id: str) -> List[str]:
        """Get list of videos user has liked"""
        try:
            db = await get_database()
            interactions_collection = db.user_video_interactions
            
            interactions = await interactions_collection.find({
                "user_id": user_id,
                "interaction_type": "like"
            }).to_list(length=None)
            
            return [interaction["video_id"] for interaction in interactions]
            
        except Exception as e:
            logger.error(f"Error getting user liked videos: {e}")
            return []
    
    async def _get_new_user_recommendations(
        self, 
        user_id: str, 
        limit: int, 
        offset: int
    ) -> List[Video]:
        """Get recommendations for new users"""
        try:
            # Get popular videos from last week
            popular_videos = await self.video_repo.get_popular_by_timeframe(
                timeframe_hours=168,  # 1 week
                limit=limit // 2
            )
            
            # Get trending videos
            trending_videos = await self.video_repo.get_trending(limit=limit // 2)
            
            # Combine and shuffle for variety
            all_videos = popular_videos + trending_videos
            random.shuffle(all_videos)
            
            # Remove duplicates
            seen_ids = set()
            unique_videos = []
            for video in all_videos:
                if str(video.id) not in seen_ids:
                    seen_ids.add(str(video.id))
                    unique_videos.append(video)
            
            return unique_videos[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error getting new user recommendations: {e}")
            return []
    
    async def _get_trending_fallback(self, limit: int, offset: int) -> List[Video]:
        """Fallback to trending videos"""
        try:
            return await self.video_repo.get_trending(limit=limit + offset)[offset:]
        except Exception as e:
            logger.error(f"Error getting trending fallback: {e}")
            return []


# Global service instance
recommendation_service = RecommendationService()