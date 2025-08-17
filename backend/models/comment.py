from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum
from .base import BaseDocument, PyObjectId


class CommentStatus(str, Enum):
    ACTIVE = "active"
    HIDDEN = "hidden"
    DELETED = "deleted"
    FLAGGED = "flagged"


class CommentMetrics(BaseModel):
    """Comment engagement metrics"""
    likes: int = Field(default=0, ge=0)
    dislikes: int = Field(default=0, ge=0)
    replies_count: int = Field(default=0, ge=0)
    reports_count: int = Field(default=0, ge=0)


class Comment(BaseDocument):
    """Comment document model"""
    # Content
    content: str = Field(..., min_length=1, max_length=2000)
    
    # Relationships
    video_id: PyObjectId
    author_id: PyObjectId
    author_username: str
    author_avatar: Optional[str] = None
    
    # Threading support
    parent_id: Optional[PyObjectId] = None  # For nested replies
    thread_id: PyObjectId  # Root comment ID for the thread
    depth: int = Field(default=0, ge=0, le=5)  # Max depth of 5 levels
    
    # Status and moderation
    status: CommentStatus = Field(default=CommentStatus.ACTIVE)
    is_pinned: bool = Field(default=False)
    is_creator_hearted: bool = Field(default=False)  # Hearted by video creator
    
    # Metrics
    metrics: CommentMetrics = Field(default_factory=CommentMetrics)
    
    # Moderation
    flagged_by: List[PyObjectId] = Field(default_factory=list)
    moderated_by: Optional[PyObjectId] = None
    moderated_at: Optional[datetime] = None
    moderation_reason: Optional[str] = None
    
    # Timestamps
    edited_at: Optional[datetime] = None
    
    @validator('content')
    def validate_content(cls, v):
        """Validate comment content"""
        v = v.strip()
        if not v:
            raise ValueError("Comment cannot be empty")
        return v
    
    @validator('depth')
    def validate_depth(cls, v):
        """Ensure comment depth doesn't exceed maximum"""
        if v > 5:
            raise ValueError("Comment depth cannot exceed 5 levels")
        return v
    
    def is_reply(self) -> bool:
        """Check if this is a reply to another comment"""
        return self.parent_id is not None
    
    def can_be_replied_to(self) -> bool:
        """Check if this comment can receive replies"""
        return self.depth < 5 and self.status == CommentStatus.ACTIVE
    
    def update_metrics(self, **kwargs):
        """Update comment metrics"""
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)


class CommentCreateRequest(BaseModel):
    """Request model for creating a comment"""
    content: str = Field(..., min_length=1, max_length=2000)
    video_id: str
    parent_id: Optional[str] = None


class CommentUpdateRequest(BaseModel):
    """Request model for updating a comment"""
    content: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    """Response model for comment data"""
    id: str
    content: str
    video_id: str
    author_id: str
    author_username: str
    author_avatar: Optional[str]
    parent_id: Optional[str]
    depth: int
    status: CommentStatus
    is_pinned: bool
    is_creator_hearted: bool
    metrics: CommentMetrics
    created_at: datetime
    updated_at: datetime
    edited_at: Optional[datetime]
    replies: List["CommentResponse"] = Field(default_factory=list)
    
    @classmethod
    def from_comment(cls, comment: Comment, replies: List["CommentResponse"] = None) -> "CommentResponse":
        """Create response from comment document"""
        return cls(
            id=str(comment.id),
            content=comment.content,
            video_id=str(comment.video_id),
            author_id=str(comment.author_id),
            author_username=comment.author_username,
            author_avatar=comment.author_avatar,
            parent_id=str(comment.parent_id) if comment.parent_id else None,
            depth=comment.depth,
            status=comment.status,
            is_pinned=comment.is_pinned,
            is_creator_hearted=comment.is_creator_hearted,
            metrics=comment.metrics,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            edited_at=comment.edited_at,
            replies=replies or []
        )


# Update forward reference
CommentResponse.model_rebuild()


class CommentTreeResponse(BaseModel):
    """Response model for comment tree with nested replies"""
    comments: List[CommentResponse]
    total_count: int
    has_more: bool
    next_cursor: Optional[str] = None


class CommentModerationRequest(BaseModel):
    """Request model for comment moderation actions"""
    action: str = Field(..., pattern=r'^(approve|hide|delete|pin|unpin|heart|unheart)$')
    reason: Optional[str] = Field(None, max_length=500)