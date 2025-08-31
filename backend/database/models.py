"""
SQLAlchemy database models for PostgreSQL
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, Float, 
    ForeignKey, Table, JSON, Enum as SQLEnum, Index, CheckConstraint,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
import uuid
import enum

from .postgres import Base

# Enums
class UserRole(str, enum.Enum):
    VIEWER = "viewer"
    CREATOR = "creator"
    MODERATOR = "moderator"
    ADMIN = "admin"

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"

class VideoCategory(str, enum.Enum):
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
    TRENDING = "trending"
    MUKBANG = "mukbang"
    DAILY = "daily"

class VideoStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    PRIVATE = "private"
    UNLISTED = "unlisted"
    REMOVED = "removed"

class CommentStatus(str, enum.Enum):
    ACTIVE = "active"
    HIDDEN = "hidden"
    DELETED = "deleted"
    FLAGGED = "flagged"

# Association tables for many-to-many relationships
user_subscriptions = Table(
    'user_subscriptions',
    Base.metadata,
    Column('subscriber_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('subscribed_to_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint('subscriber_id', 'subscribed_to_id')
)

user_blocked = Table(
    'user_blocked',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('blocked_user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint('user_id', 'blocked_user_id')
)

video_likes = Table(
    'video_likes',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('video_id', UUID(as_uuid=True), ForeignKey('videos.id'), primary_key=True),
    Column('is_like', Boolean, default=True),  # True for like, False for dislike
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint('user_id', 'video_id')
)

comment_likes = Table(
    'comment_likes',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('comment_id', UUID(as_uuid=True), ForeignKey('comments.id'), primary_key=True),
    Column('is_like', Boolean, default=True),  # True for like, False for dislike
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint('user_id', 'comment_id')
)

class User(Base):
    __tablename__ = "users"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    bio: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Authentication
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verification_token: Mapped[Optional[str]] = mapped_column(String(255))
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255))
    password_reset_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # User role and status
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.VIEWER)
    status: Mapped[UserStatus] = mapped_column(SQLEnum(UserStatus), default=UserStatus.ACTIVE)
    
    # Profile information
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    country: Mapped[Optional[str]] = mapped_column(String(3))  # ISO country code
    timezone: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Settings and preferences (JSON column)
    preferences: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Statistics (JSON column)
    stats: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Channel information
    channel_name: Mapped[Optional[str]] = mapped_column(String(100))
    channel_description: Mapped[Optional[str]] = mapped_column(Text)
    channel_banner_url: Mapped[Optional[str]] = mapped_column(Text)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # OAuth integration
    oauth_providers: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    
    # Two-Factor Authentication
    tfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    tfa_secret: Mapped[Optional[str]] = mapped_column(String(255))
    tfa_backup_codes: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    tfa_setup_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    tfa_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    tfa_disabled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    tfa_backup_codes_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_video_upload: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    videos: Mapped[List["Video"]] = relationship("Video", back_populates="channel_owner", cascade="all, delete-orphan")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    
    # Many-to-many relationships
    subscriptions: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_subscriptions,
        primaryjoin=id == user_subscriptions.c.subscriber_id,
        secondaryjoin=id == user_subscriptions.c.subscribed_to_id,
        back_populates="subscribers"
    )
    
    subscribers: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_subscriptions,
        primaryjoin=id == user_subscriptions.c.subscribed_to_id,
        secondaryjoin=id == user_subscriptions.c.subscriber_id,
        back_populates="subscriptions"
    )
    
    blocked_users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_blocked,
        primaryjoin=id == user_blocked.c.user_id,
        secondaryjoin=id == user_blocked.c.blocked_user_id
    )
    
    # Indexes
    __table_args__ = (
        Index('ix_users_username', 'username'),
        Index('ix_users_email', 'email'),
        Index('ix_users_channel_name', 'channel_name'),
        Index('ix_users_status', 'status'),
        Index('ix_users_created_at', 'created_at'),
        CheckConstraint('char_length(username) >= 3', name='username_min_length'),
        CheckConstraint('char_length(email) >= 5', name='email_min_length'),
    )

class Video(Base):
    __tablename__ = "videos"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Channel information
    channel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    channel_name: Mapped[str] = mapped_column(String(100), nullable=False)
    channel_avatar: Mapped[Optional[str]] = mapped_column(Text)
    
    # Video content
    video_url: Mapped[str] = mapped_column(Text, nullable=False)
    youtube_embed_url: Mapped[Optional[str]] = mapped_column(Text)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    thumbnails: Mapped[Optional[List[dict]]] = mapped_column(JSON)
    
    # Categorization
    category: Mapped[VideoCategory] = mapped_column(SQLEnum(VideoCategory), default=VideoCategory.ENTERTAINMENT)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    language: Mapped[str] = mapped_column(String(10), default='en')
    
    # Status and visibility
    status: Mapped[VideoStatus] = mapped_column(SQLEnum(VideoStatus), default=VideoStatus.PUBLISHED)
    is_live: Mapped[bool] = mapped_column(Boolean, default=False)
    scheduled_publish_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Metrics
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    dislikes: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    watch_time_minutes: Mapped[float] = mapped_column(Float, default=0.0)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Technical specs (JSON column)
    quality: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # SEO and discovery
    search_keywords: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    trending_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Content settings
    age_restriction: Mapped[Optional[int]] = mapped_column(Integer)
    content_warnings: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    monetization_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    channel_owner: Mapped["User"] = relationship("User", back_populates="videos")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="video", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('ix_videos_channel_id', 'channel_id'),
        Index('ix_videos_category', 'category'),
        Index('ix_videos_status', 'status'),
        Index('ix_videos_created_at', 'created_at'),
        Index('ix_videos_views', 'views'),
        Index('ix_videos_trending_score', 'trending_score'),
        Index('ix_videos_title_fulltext', 'title'),
        CheckConstraint('duration_seconds > 0', name='duration_positive'),
        CheckConstraint('views >= 0', name='views_non_negative'),
        CheckConstraint('likes >= 0', name='likes_non_negative'),
        CheckConstraint('dislikes >= 0', name='dislikes_non_negative'),
    )

class Comment(Base):
    __tablename__ = "comments"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Relationships
    video_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('videos.id'), nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    author_username: Mapped[str] = mapped_column(String(30), nullable=False)
    author_avatar: Mapped[Optional[str]] = mapped_column(Text)
    
    # Threading support
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('comments.id'))
    thread_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    depth: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status and moderation
    status: Mapped[CommentStatus] = mapped_column(SQLEnum(CommentStatus), default=CommentStatus.ACTIVE)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_creator_hearted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metrics
    likes: Mapped[int] = mapped_column(Integer, default=0)
    dislikes: Mapped[int] = mapped_column(Integer, default=0)
    replies_count: Mapped[int] = mapped_column(Integer, default=0)
    reports_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Moderation
    flagged_by: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    moderated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    moderated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    moderation_reason: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    edited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="comments")
    author: Mapped["User"] = relationship("User", back_populates="comments")
    parent: Mapped[Optional["Comment"]] = relationship("Comment", remote_side=[id])
    moderator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[moderated_by])
    
    # Indexes
    __table_args__ = (
        Index('ix_comments_video_id', 'video_id'),
        Index('ix_comments_author_id', 'author_id'),
        Index('ix_comments_parent_id', 'parent_id'),
        Index('ix_comments_thread_id', 'thread_id'),
        Index('ix_comments_status', 'status'),
        Index('ix_comments_created_at', 'created_at'),
        CheckConstraint('depth >= 0 AND depth <= 5', name='depth_range'),
        CheckConstraint('likes >= 0', name='comment_likes_non_negative'),
        CheckConstraint('dislikes >= 0', name='comment_dislikes_non_negative'),
        CheckConstraint('char_length(content) >= 1', name='content_not_empty'),
    )