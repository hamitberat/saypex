from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
from .base import BaseDocument, PyObjectId


class VideoCategory(str, Enum):
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    GAMING = "gaming"
    MUSIC = "music"
    NEWS = "news"
    SPORTS = "sports"
    TECHNOLOGY = "technology"
    LIFESTYLE = "lifestyle"
    COOKING = "cooking"
    TRAVEL = "travel"


class VideoStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    PRIVATE = "private"
    UNLISTED = "unlisted"
    REMOVED = "removed"


class VideoMetrics(BaseModel):
    """Video engagement metrics"""
    views: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)
    dislikes: int = Field(default=0, ge=0)
    comments_count: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    watch_time_minutes: float = Field(default=0.0, ge=0)
    engagement_rate: float = Field(default=0.0, ge=0, le=1)
    
    def calculate_engagement_rate(self):
        """Calculate engagement rate based on interactions vs views"""
        if self.views == 0:
            return 0.0
        interactions = self.likes + self.dislikes + self.comments_count + self.shares
        return min(interactions / self.views, 1.0)


class VideoThumbnail(BaseModel):
    """Video thumbnail information"""
    url: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    size_bytes: Optional[int] = Field(default=None, ge=0)


class VideoQuality(BaseModel):
    """Video quality and technical specs"""
    resolution: str  # e.g., "1080p", "720p", "480p"
    bitrate: Optional[int] = Field(default=None, ge=0)
    fps: Optional[int] = Field(default=30, ge=1, le=120)
    codec: Optional[str] = Field(default="h264")
    file_size_mb: Optional[float] = Field(default=None, ge=0)


class Video(BaseDocument):
    """Main video document model"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default="", max_length=5000)
    
    # Channel information
    channel_id: PyObjectId
    channel_name: str = Field(..., min_length=1, max_length=100)
    channel_avatar: Optional[str] = None
    
    # Video content
    video_url: str  # URL to actual video file
    youtube_embed_url: Optional[str] = None  # For embedded YouTube videos
    duration_seconds: int = Field(..., ge=1)
    thumbnails: List[VideoThumbnail] = Field(default_factory=list)
    
    # Categorization
    category: VideoCategory = Field(default=VideoCategory.ENTERTAINMENT)
    tags: List[str] = Field(default_factory=list, max_items=20)
    language: str = Field(default="en")
    
    # Status and visibility
    status: VideoStatus = Field(default=VideoStatus.PUBLISHED)
    is_live: bool = Field(default=False)
    scheduled_publish_at: Optional[datetime] = None
    
    # Metrics and analytics
    metrics: VideoMetrics = Field(default_factory=VideoMetrics)
    
    # Technical specs
    quality: Optional[VideoQuality] = None
    
    # SEO and discovery
    search_keywords: List[str] = Field(default_factory=list)
    trending_score: float = Field(default=0.0, ge=0)
    
    # Regional and content settings
    age_restriction: Optional[int] = Field(default=None, ge=0, le=18)
    content_warnings: List[str] = Field(default_factory=list)
    monetization_enabled: bool = Field(default=True)
    
    @validator('tags', 'search_keywords')
    def normalize_tags(cls, v):
        """Normalize tags to lowercase"""
        return [tag.lower().strip() for tag in v if tag.strip()]
    
    @validator('duration_seconds')
    def validate_duration(cls, v):
        """Ensure duration is reasonable (max 12 hours)"""
        if v > 43200:  # 12 hours in seconds
            raise ValueError("Video duration cannot exceed 12 hours")
        return v
    
    def get_primary_thumbnail(self) -> Optional[VideoThumbnail]:
        """Get the highest quality thumbnail"""
        if not self.thumbnails:
            return None
        return max(self.thumbnails, key=lambda x: x.width * x.height)
    
    def get_formatted_duration(self) -> str:
        """Get duration in HH:MM:SS format"""
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"
    
    def update_metrics(self, **kwargs):
        """Update video metrics and recalculate derived values"""
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)
        
        # Recalculate engagement rate
        self.metrics.engagement_rate = self.metrics.calculate_engagement_rate()
        
        # Update trending score based on recent engagement
        self.update_trending_score()
    
    def update_trending_score(self):
        """Calculate trending score based on recent engagement"""
        # Simple trending algorithm - can be enhanced with ML
        age_hours = (datetime.utcnow() - self.created_at).total_seconds() / 3600
        age_penalty = max(0.1, 1 / (1 + age_hours / 24))  # Decay over time
        
        engagement_score = (
            self.metrics.likes * 1.0 +
            self.metrics.comments_count * 2.0 +
            self.metrics.shares * 3.0 +
            self.metrics.views * 0.1
        )
        
        self.trending_score = engagement_score * age_penalty


class VideoCreateRequest(BaseModel):
    """Request model for creating a new video"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default="", max_length=5000)
    channel_id: str
    video_url: str
    youtube_embed_url: Optional[str] = None
    duration_seconds: int = Field(..., ge=1)
    category: VideoCategory = Field(default=VideoCategory.ENTERTAINMENT)
    tags: List[str] = Field(default_factory=list, max_items=20)
    thumbnails: List[VideoThumbnail] = Field(default_factory=list)
    status: VideoStatus = Field(default=VideoStatus.PUBLISHED)


class VideoUpdateRequest(BaseModel):
    """Request model for updating video"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    category: Optional[VideoCategory] = None
    tags: Optional[List[str]] = Field(None, max_items=20)
    status: Optional[VideoStatus] = None


class VideoResponse(BaseModel):
    """Response model for video data"""
    id: str
    title: str
    description: str
    channel_id: str
    channel_name: str
    channel_avatar: Optional[str]
    video_url: str
    youtube_embed_url: Optional[str]
    duration: str  # Formatted duration
    duration_seconds: int
    thumbnails: List[VideoThumbnail]
    category: VideoCategory
    tags: List[str]
    status: VideoStatus
    metrics: VideoMetrics
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_video(cls, video: Video) -> "VideoResponse":
        """Create response from video document"""
        return cls(
            id=str(video.id),
            title=video.title,
            description=video.description or "",
            channel_id=str(video.channel_id),
            channel_name=video.channel_name,
            channel_avatar=video.channel_avatar,
            video_url=video.video_url,
            youtube_embed_url=video.youtube_embed_url,
            duration=video.get_formatted_duration(),
            duration_seconds=video.duration_seconds,
            thumbnails=video.thumbnails,
            category=video.category,
            tags=video.tags,
            status=video.status,
            metrics=video.metrics,
            created_at=video.created_at,
            updated_at=video.updated_at
        )