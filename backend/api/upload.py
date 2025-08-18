from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, status
from typing import List, Optional
import logging

from ..models.video import VideoResponse, VideoCategory
from ..models.user import UserResponse
from ..services.upload_service import upload_service
from ..middleware.auth import require_auth, require_creator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/video", response_model=VideoResponse)
async def upload_video(
    title: str = Form(..., min_length=1, max_length=200),
    description: str = Form("", max_length=5000),
    category: VideoCategory = Form(VideoCategory.ENTERTAINMENT),
    tags: str = Form(""),  # Comma-separated tags
    video_file: UploadFile = File(...),
    thumbnail_file: Optional[UploadFile] = File(None),
    current_user: UserResponse = Depends(require_creator)
):
    """
    Upload a new video
    MODULAR API ENDPOINT: Delegates to upload_service for business logic
    """
    try:
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        
        # Validate required fields
        if not title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title is required"
            )
        
        if not video_file or not video_file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Video file is required"
            )
        
        # Upload video using service layer
        video_response = await upload_service.upload_video(
            user_id=current_user.id,
            video_file=video_file,
            title=title,
            description=description,
            category=category,
            tags=tag_list,
            thumbnail_file=thumbnail_file
        )
        
        if not video_response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload video"
            )
        
        return video_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload video endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload video"
        )


@router.get("/my-videos", response_model=List[VideoResponse])
async def get_my_uploads(
    limit: int = 50,
    offset: int = 0,
    current_user: UserResponse = Depends(require_auth)
):
    """
    Get current user's uploaded videos
    """
    try:
        videos = await upload_service.get_user_uploads(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        return videos
        
    except Exception as e:
        logger.error(f"Error getting user uploads: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get uploads"
        )


@router.delete("/video/{video_id}")
async def delete_my_video(
    video_id: str,
    current_user: UserResponse = Depends(require_auth)
):
    """
    Delete a video uploaded by current user
    """
    try:
        success = await upload_service.delete_video(video_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found or not authorized"
            )
        
        return {"message": "Video deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete video"
        )


@router.get("/formats")
async def get_supported_formats():
    """
    Get list of supported video formats
    """
    return {
        "video_formats": [".mp4", ".avi", ".mov", ".mkv", ".webm"],
        "thumbnail_formats": [".jpg", ".jpeg", ".png", ".webp"],
        "max_file_size_mb": 500,
        "max_title_length": 200,
        "max_description_length": 5000
    }