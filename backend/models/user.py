from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum
from .base import BaseDocument, PyObjectId


class UserRole(str, Enum):
    VIEWER = "viewer"
    CREATOR = "creator"
    MODERATOR = "moderator"
    ADMIN = "admin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"


class UserPreferences(BaseModel):
    """User preferences and settings"""
    language: str = Field(default="en")
    theme: str = Field(default="light")  # light, dark, auto
    autoplay: bool = Field(default=True)
    notifications_enabled: bool = Field(default=True)
    email_notifications: bool = Field(default=True)
    content_filter: str = Field(default="moderate")  # strict, moderate, none
    preferred_quality: str = Field(default="auto")  # auto, 1080p, 720p, 480p
    
    # Privacy settings
    show_subscriptions: bool = Field(default=True)
    show_playlists: bool = Field(default=True)
    show_liked_videos: bool = Field(default=False)


class UserStats(BaseModel):
    """User statistics and metrics"""
    total_watch_time_minutes: float = Field(default=0.0, ge=0)
    videos_watched: int = Field(default=0, ge=0)
    subscriptions_count: int = Field(default=0, ge=0)
    subscribers_count: int = Field(default=0, ge=0)
    videos_uploaded: int = Field(default=0, ge=0)
    total_video_views: int = Field(default=0, ge=0)
    likes_given: int = Field(default=0, ge=0)
    comments_made: int = Field(default=0, ge=0)
    last_active: Optional[datetime] = None


class User(BaseDocument):
    """User document model"""
    # Basic information
    username: str = Field(..., min_length=3, max_length=30, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    
    # Authentication
    password_hash: str  # Will be hashed before storing
    is_email_verified: bool = Field(default=False)
    email_verification_token: Optional[str] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    
    # User role and status
    role: UserRole = Field(default=UserRole.VIEWER)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    
    # Profile information
    date_of_birth: Optional[datetime] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    
    # Settings and preferences
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    
    # Statistics
    stats: UserStats = Field(default_factory=UserStats)
    
    # Social connections
    subscribed_channels: List[PyObjectId] = Field(default_factory=list)
    blocked_users: List[PyObjectId] = Field(default_factory=list)
    
    # Channel information (if user is a creator)
    channel_id: Optional[PyObjectId] = None
    channel_name: Optional[str] = None
    channel_description: Optional[str] = None
    channel_banner_url: Optional[str] = None
    is_verified: bool = Field(default=False)
    
    # Timestamps
    last_login: Optional[datetime] = None
    last_video_upload: Optional[datetime] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v.lower()
    
    @validator('email')
    def email_lowercase(cls, v):
        return v.lower()
    
    def is_channel_owner(self) -> bool:
        """Check if user owns a channel"""
        return self.channel_id is not None
    
    def can_upload_videos(self) -> bool:
        """Check if user can upload videos"""
        return (
            self.role in [UserRole.CREATOR, UserRole.ADMIN] and
            self.status == UserStatus.ACTIVE and
            self.is_email_verified
        )
    
    def update_stats(self, **kwargs):
        """Update user statistics"""
        for key, value in kwargs.items():
            if hasattr(self.stats, key):
                if key in ['total_watch_time_minutes', 'videos_watched', 'likes_given', 'comments_made']:
                    # Increment counters
                    current_value = getattr(self.stats, key)
                    setattr(self.stats, key, current_value + value)
                else:
                    setattr(self.stats, key, value)
        
        self.stats.last_active = datetime.utcnow()


class UserCreateRequest(BaseModel):
    """Request model for user registration"""
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[datetime] = None
    country: Optional[str] = None


class UserLoginRequest(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    """Request model for updating user profile"""
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    preferences: Optional[UserPreferences] = None


class UserResponse(BaseModel):
    """Response model for user data"""
    id: str
    username: str
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    role: UserRole
    status: UserStatus
    is_verified: bool
    channel_id: Optional[str]
    channel_name: Optional[str]
    stats: UserStats
    created_at: datetime
    
    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        """Create response from user document"""
        return cls(
            id=str(user.id),
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            role=user.role,
            status=user.status,
            is_verified=user.is_verified,
            channel_id=str(user.channel_id) if user.channel_id else None,
            channel_name=user.channel_name,
            stats=user.stats,
            created_at=user.created_at
        )


class PublicUserResponse(BaseModel):
    """Public response model for user data (limited info)"""
    id: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    is_verified: bool
    channel_name: Optional[str]
    subscribers_count: int
    
    @classmethod
    def from_user(cls, user: User) -> "PublicUserResponse":
        """Create public response from user document"""
        return cls(
            id=str(user.id),
            username=user.username,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            is_verified=user.is_verified,
            channel_name=user.channel_name,
            subscribers_count=user.stats.subscribers_count
        )