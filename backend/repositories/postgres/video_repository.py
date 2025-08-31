"""
PostgreSQL Video Repository
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete, func, and_, or_, desc, text
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime

from database.models import Video, VideoStatus, VideoCategory, User
from models.video import VideoCreateRequest, VideoUpdateRequest


class PostgreSQLVideoRepository:
    """PostgreSQL implementation of Video Repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_video(self, video_data: VideoCreateRequest, channel_id: uuid.UUID) -> Video:
        """Create a new video"""
        try:
            # Get channel information
            channel_stmt = select(User).where(User.id == channel_id)
            channel_result = await self.session.execute(channel_stmt)
            channel = channel_result.scalar_one_or_none()
            
            if not channel:
                raise ValueError("Channel not found")
            
            db_video = Video(
                title=video_data.title,
                description=video_data.description or "",
                channel_id=channel_id,
                channel_name=channel.channel_name or channel.username,
                channel_avatar=channel.avatar_url,
                video_url=video_data.video_url,
                youtube_embed_url=video_data.youtube_embed_url,
                duration_seconds=video_data.duration_seconds,
                thumbnails=[thumb.dict() for thumb in video_data.thumbnails],
                category=video_data.category,
                tags=video_data.tags or [],
                status=video_data.status,
                search_keywords=video_data.tags or []
            )
            
            self.session.add(db_video)
            await self.session.flush()
            
            # Update user stats
            await self._update_channel_stats(channel_id, videos_uploaded=1)
            
            return db_video
            
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError("Video creation failed")
    
    async def get_video_by_id(self, video_id: uuid.UUID) -> Optional[Video]:
        """Get video by ID"""
        stmt = select(Video).where(
            and_(Video.id == video_id, Video.status != VideoStatus.REMOVED)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_videos(self, 
                        limit: int = 20, 
                        offset: int = 0, 
                        category: Optional[VideoCategory] = None,
                        status: VideoStatus = VideoStatus.PUBLISHED) -> List[Video]:
        """Get videos with optional filters"""
        conditions = [Video.status == status]
        
        if category:
            conditions.append(Video.category == category)
        
        stmt = select(Video).where(and_(*conditions)).order_by(
            desc(Video.created_at)
        ).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_trending_videos(self, limit: int = 20, offset: int = 0) -> List[Video]:
        """Get trending videos"""
        stmt = select(Video).where(
            and_(
                Video.status == VideoStatus.PUBLISHED,
                Video.trending_score > 0
            )
        ).order_by(desc(Video.trending_score)).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def search_videos(self, 
                           query: str, 
                           limit: int = 20, 
                           offset: int = 0,
                           category: Optional[VideoCategory] = None) -> List[Video]:
        """Search videos by title and description"""
        search_term = f"%{query.lower()}%"
        conditions = [
            Video.status == VideoStatus.PUBLISHED,
            or_(
                Video.title.ilike(search_term),
                Video.description.ilike(search_term),
                func.array_to_string(Video.tags, ' ').ilike(search_term)
            )
        ]
        
        if category:
            conditions.append(Video.category == category)
        
        stmt = select(Video).where(and_(*conditions)).order_by(
            desc(Video.views), desc(Video.created_at)
        ).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_videos_by_channel(self, 
                                   channel_id: uuid.UUID, 
                                   limit: int = 20, 
                                   offset: int = 0) -> List[Video]:
        """Get videos by channel"""
        stmt = select(Video).where(
            and_(
                Video.channel_id == channel_id,
                Video.status.in_([VideoStatus.PUBLISHED, VideoStatus.UNLISTED])
            )
        ).order_by(desc(Video.created_at)).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def update_video(self, video_id: uuid.UUID, video_data: VideoUpdateRequest) -> Optional[Video]:
        """Update video information"""
        try:
            update_data = {}
            
            if video_data.title:
                update_data['title'] = video_data.title
            if video_data.description is not None:
                update_data['description'] = video_data.description
            if video_data.category:
                update_data['category'] = video_data.category
            if video_data.tags is not None:
                update_data['tags'] = video_data.tags
                update_data['search_keywords'] = video_data.tags
            if video_data.status:
                update_data['status'] = video_data.status
            
            if update_data:
                update_data['updated_at'] = func.now()
                stmt = update(Video).where(Video.id == video_id).values(**update_data)
                await self.session.execute(stmt)
            
            return await self.get_video_by_id(video_id)
            
        except Exception as e:
            await self.session.rollback()
            raise ValueError("Video update failed")
    
    async def delete_video(self, video_id: uuid.UUID) -> bool:
        """Delete video (soft delete)"""
        stmt = update(Video).where(Video.id == video_id).values(
            status=VideoStatus.REMOVED,
            updated_at=func.now()
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def increment_views(self, video_id: uuid.UUID) -> bool:
        """Increment video view count"""
        stmt = update(Video).where(Video.id == video_id).values(
            views=Video.views + 1,
            updated_at=func.now()
        )
        result = await self.session.execute(stmt)
        
        if result.rowcount > 0:
            # Update trending score
            await self._update_trending_score(video_id)
            return True
        return False
    
    async def update_metrics(self, video_id: uuid.UUID, **metrics) -> bool:
        """Update video metrics"""
        valid_metrics = {}
        for key, value in metrics.items():
            if hasattr(Video, key) and key in ['likes', 'dislikes', 'shares', 'watch_time_minutes']:
                valid_metrics[key] = value
        
        if valid_metrics:
            valid_metrics['updated_at'] = func.now()
            stmt = update(Video).where(Video.id == video_id).values(**valid_metrics)
            result = await self.session.execute(stmt)
            
            if result.rowcount > 0:
                await self._update_trending_score(video_id)
                return True
        return False
    
    async def get_recommended_videos(self, 
                                   user_id: Optional[uuid.UUID] = None,
                                   video_id: Optional[uuid.UUID] = None,
                                   limit: int = 10) -> List[Video]:
        """Get recommended videos"""
        # Simple recommendation: popular videos in same categories
        conditions = [Video.status == VideoStatus.PUBLISHED]
        
        if video_id:
            # Get videos from same category
            current_video_stmt = select(Video.category).where(Video.id == video_id)
            current_video_result = await self.session.execute(current_video_stmt)
            category = current_video_result.scalar_one_or_none()
            
            if category:
                conditions.append(Video.category == category)
                conditions.append(Video.id != video_id)
        
        stmt = select(Video).where(and_(*conditions)).order_by(
            desc(Video.engagement_rate),
            desc(Video.views),
            desc(Video.created_at)
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_popular_videos(self, 
                               time_range: str = "week",
                               limit: int = 20,
                               offset: int = 0) -> List[Video]:
        """Get popular videos in time range"""
        # Calculate date threshold
        if time_range == "day":
            threshold = func.now() - text("INTERVAL '1 day'")
        elif time_range == "week":
            threshold = func.now() - text("INTERVAL '7 days'")
        elif time_range == "month":
            threshold = func.now() - text("INTERVAL '30 days'")
        else:
            threshold = func.now() - text("INTERVAL '365 days'")
        
        stmt = select(Video).where(
            and_(
                Video.status == VideoStatus.PUBLISHED,
                Video.created_at >= threshold
            )
        ).order_by(
            desc(Video.views),
            desc(Video.likes),
            desc(Video.engagement_rate)
        ).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def count_videos(self, 
                          channel_id: Optional[uuid.UUID] = None,
                          status: Optional[VideoStatus] = None) -> int:
        """Count videos with filters"""
        conditions = []
        
        if channel_id:
            conditions.append(Video.channel_id == channel_id)
        if status:
            conditions.append(Video.status == status)
        
        if conditions:
            stmt = select(func.count(Video.id)).where(and_(*conditions))
        else:
            stmt = select(func.count(Video.id))
        
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def get_video_analytics(self, video_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Get detailed video analytics"""
        video = await self.get_video_by_id(video_id)
        if not video:
            return None
        
        return {
            "id": str(video.id),
            "title": video.title,
            "views": video.views,
            "likes": video.likes,
            "dislikes": video.dislikes,
            "comments_count": video.comments_count,
            "shares": video.shares,
            "watch_time_minutes": video.watch_time_minutes,
            "engagement_rate": video.engagement_rate,
            "trending_score": video.trending_score,
            "created_at": video.created_at,
            "updated_at": video.updated_at
        }
    
    async def _update_trending_score(self, video_id: uuid.UUID):
        """Update trending score for a video"""
        video = await self.get_video_by_id(video_id)
        if not video:
            return
        
        # Calculate trending score
        age_hours = (datetime.utcnow() - video.created_at.replace(tzinfo=None)).total_seconds() / 3600
        age_penalty = max(0.1, 1 / (1 + age_hours / 24))
        
        engagement_score = (
            video.likes * 1.0 +
            video.comments_count * 2.0 +
            video.shares * 3.0 +
            video.views * 0.1
        )
        
        trending_score = engagement_score * age_penalty
        
        stmt = update(Video).where(Video.id == video_id).values(
            trending_score=trending_score,
            engagement_rate=self._calculate_engagement_rate(video)
        )
        await self.session.execute(stmt)
    
    def _calculate_engagement_rate(self, video: Video) -> float:
        """Calculate engagement rate"""
        if video.views == 0:
            return 0.0
        interactions = video.likes + video.dislikes + video.comments_count + video.shares
        return min(interactions / video.views, 1.0)
    
    async def _update_channel_stats(self, channel_id: uuid.UUID, **stats):
        """Update channel statistics"""
        user_stmt = select(User).where(User.id == channel_id)
        user_result = await self.session.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if user and user.stats:
            current_stats = user.stats.copy()
            for key, value in stats.items():
                if key in current_stats:
                    current_stats[key] = current_stats.get(key, 0) + value
            
            user_update_stmt = update(User).where(User.id == channel_id).values(stats=current_stats)
            await self.session.execute(user_update_stmt)