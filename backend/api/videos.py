from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
import logging

from ..models.video import (
    VideoResponse, VideoCreateRequest, VideoUpdateRequest, VideoCategory
)
from ..models.user import UserResponse
from ..services.video_service import video_service
from ..middleware.auth import require_auth, require_creator, optional_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/videos", tags=["videos"])


@router.get("/", response_model=List[VideoResponse])
async def get_videos(
    category: Optional[VideoCategory] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100, description="Number of videos to return"),
    offset: int = Query(0, ge=0, description="Number of videos to skip"),
    current_user: Optional[UserResponse] = optional_auth()
):
    """Get videos for home page with optional filtering"""
    try:
        user_id = current_user.id if current_user else None
        videos = await video_service.get_home_videos(
            category=category,
            limit=limit,
            offset=offset,
            user_id=user_id
        )
        return videos
    except Exception as e:
        logger.error(f"Error getting videos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get videos"
        )


@router.post("/", response_model=VideoResponse)
async def create_video(
    video_data: VideoCreateRequest,
    current_user: UserResponse = Depends(require_creator)
):
    """Create a new video"""
    try:
        video = await video_service.create_video(video_data, current_user.id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create video"
            )
        return video
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating video: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create video"
        )


@router.get("/search", response_model=List[VideoResponse])
async def search_videos(
    q: str = Query(..., description="Search query"),
    category: Optional[VideoCategory] = Query(None, description="Filter by category"),
    sort_by: str = Query("relevance", description="Sort by: relevance, date, views, likes"),
    limit: int = Query(50, ge=1, le=100, description="Number of videos to return"),
    offset: int = Query(0, ge=0, description="Number of videos to skip")
):
    """Search videos"""
    try:
        videos = await video_service.search_videos(
            query=q,
            category=category,
            sort_by=sort_by,
            limit=limit,
            offset=offset
        )
        return videos
    except Exception as e:
        logger.error(f"Error searching videos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search videos"
        )


@router.get("/trending", response_model=List[VideoResponse])
async def get_trending_videos(
    category: Optional[VideoCategory] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100, description="Number of videos to return")
):
    """Get trending videos"""
    try:
        videos = await video_service.get_trending_videos(category=category, limit=limit)
        return videos
    except Exception as e:
        logger.error(f"Error getting trending videos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trending videos"
        )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    current_user: Optional[UserResponse] = optional_auth()
):
    """Get video by ID"""
    try:
        user_id = current_user.id if current_user else None
        video = await video_service.get_video(video_id, user_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        return video
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get video"
        )


@router.put("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: str,
    update_data: VideoUpdateRequest,
    current_user: UserResponse = Depends(require_auth)
):
    """Update video"""
    try:
        video = await video_service.update_video(video_id, update_data, current_user.id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found or access denied"
            )
        return video
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update video"
        )


@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    current_user: UserResponse = Depends(require_auth)
):
    """Delete video"""
    try:
        success = await video_service.delete_video(video_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found or access denied"
            )
        return {"message": "Video deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete video"
        )


@router.get("/{video_id}/recommendations", response_model=List[VideoResponse])
async def get_video_recommendations(
    video_id: str,
    limit: int = Query(20, ge=1, le=50, description="Number of recommendations")
):
    """Get recommended videos for video player"""
    try:
        videos = await video_service.get_recommended_videos(video_id, limit)
        return videos
    except Exception as e:
        logger.error(f"Error getting video recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendations"
        )


@router.post("/{video_id}/like")
async def like_video(
    video_id: str,
    current_user: UserResponse = Depends(require_auth)
):
    """Like a video"""
    try:
        success = await video_service.like_video(video_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot like video (already liked or video not found)"
            )
        return {"message": "Video liked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error liking video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to like video"
        )


@router.post("/{video_id}/dislike")
async def dislike_video(
    video_id: str,
    current_user: UserResponse = Depends(require_auth)
):
    """Dislike a video"""
    try:
        success = await video_service.dislike_video(video_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot dislike video (already disliked or video not found)"
            )
        return {"message": "Video disliked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disliking video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to dislike video"
        )


@router.delete("/{video_id}/reaction")
async def remove_video_reaction(
    video_id: str,
    current_user: UserResponse = Depends(require_auth)
):
    """Remove like/dislike from video"""
    try:
        success = await video_service.remove_video_reaction(video_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No reaction to remove"
            )
        return {"message": "Reaction removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing video reaction {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove reaction"
        )