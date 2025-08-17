from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
import logging

from ..models.comment import (
    CommentResponse, CommentTreeResponse, CommentCreateRequest,
    CommentUpdateRequest, CommentModerationRequest
)
from ..models.user import UserResponse
from ..services.comment_service import comment_service
from ..middleware.auth import require_auth, require_moderator, optional_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/video/{video_id}", response_model=CommentTreeResponse)
async def get_video_comments(
    video_id: str,
    limit: int = Query(50, ge=1, le=100, description="Number of comments to return"),
    offset: int = Query(0, ge=0, description="Number of comments to skip"),
    sort_by: str = Query("created_at", description="Sort by: created_at, likes"),
    include_replies: bool = Query(True, description="Include replies to comments")
):
    """Get comments for a video"""
    try:
        comments = await comment_service.get_video_comments(
            video_id=video_id,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            include_replies=include_replies
        )
        return comments
    except Exception as e:
        logger.error(f"Error getting video comments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get comments"
        )


@router.post("/", response_model=CommentResponse)
async def create_comment(
    comment_data: CommentCreateRequest,
    current_user: UserResponse = Depends(require_auth)
):
    """Create a new comment"""
    try:
        comment = await comment_service.create_comment(comment_data, current_user.id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create comment"
            )
        return comment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating comment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create comment"
        )


@router.get("/{comment_id}/replies", response_model=List[CommentResponse])
async def get_comment_replies(
    comment_id: str,
    limit: int = Query(20, ge=1, le=50, description="Number of replies to return"),
    offset: int = Query(0, ge=0, description="Number of replies to skip")
):
    """Get replies to a specific comment"""
    try:
        replies = await comment_service.get_comment_replies(
            parent_id=comment_id,
            limit=limit,
            offset=offset
        )
        return replies
    except Exception as e:
        logger.error(f"Error getting comment replies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get replies"
        )


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    update_data: CommentUpdateRequest,
    current_user: UserResponse = Depends(require_auth)
):
    """Update a comment"""
    try:
        comment = await comment_service.update_comment(
            comment_id, update_data, current_user.id
        )
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found or access denied"
            )
        return comment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update comment"
        )


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: UserResponse = Depends(require_auth)
):
    """Delete a comment"""
    try:
        success = await comment_service.delete_comment(comment_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found or access denied"
            )
        return {"message": "Comment deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete comment"
        )


@router.post("/{comment_id}/like")
async def like_comment(
    comment_id: str,
    current_user: UserResponse = Depends(require_auth)
):
    """Like a comment"""
    try:
        success = await comment_service.like_comment(comment_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot like comment (already liked or comment not found)"
            )
        return {"message": "Comment liked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error liking comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to like comment"
        )


@router.delete("/{comment_id}/like")
async def unlike_comment(
    comment_id: str,
    current_user: UserResponse = Depends(require_auth)
):
    """Remove like from comment"""
    try:
        success = await comment_service.unlike_comment(comment_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment not liked or not found"
            )
        return {"message": "Like removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unliking comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove like"
        )


@router.post("/{comment_id}/pin")
async def pin_comment(
    comment_id: str,
    current_user: UserResponse = Depends(require_auth)
):
    """Pin a comment (channel owner only)"""
    try:
        success = await comment_service.pin_comment(comment_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot pin comment (not channel owner or comment not found)"
            )
        return {"message": "Comment pinned successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pinning comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pin comment"
        )


@router.post("/{comment_id}/heart")
async def heart_comment(
    comment_id: str,
    current_user: UserResponse = Depends(require_auth)
):
    """Heart a comment (channel owner only)"""
    try:
        success = await comment_service.heart_comment(comment_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot heart comment (not channel owner or comment not found)"
            )
        return {"message": "Comment hearted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error hearting comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to heart comment"
        )


@router.post("/{comment_id}/flag")
async def flag_comment(
    comment_id: str,
    current_user: UserResponse = Depends(require_auth)
):
    """Flag a comment for review"""
    try:
        success = await comment_service.flag_comment(comment_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot flag comment or comment not found"
            )
        return {"message": "Comment flagged successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error flagging comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to flag comment"
        )


@router.post("/{comment_id}/moderate")
async def moderate_comment(
    comment_id: str,
    moderation_data: CommentModerationRequest,
    current_user: UserResponse = Depends(require_moderator)
):
    """Moderate a comment (moderator/admin only)"""
    try:
        success = await comment_service.moderate_comment(
            comment_id, moderation_data, current_user.id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to moderate comment"
            )
        return {"message": f"Comment {moderation_data.action} successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moderating comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to moderate comment"
        )


@router.get("/user/{user_id}", response_model=List[CommentResponse])
async def get_user_comments(
    user_id: str,
    limit: int = Query(50, ge=1, le=100, description="Number of comments to return"),
    offset: int = Query(0, ge=0, description="Number of comments to skip")
):
    """Get comments by a specific user"""
    try:
        comments = await comment_service.get_user_comments(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        return comments
    except Exception as e:
        logger.error(f"Error getting user comments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user comments"
        )