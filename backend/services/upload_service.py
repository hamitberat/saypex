from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import UploadFile, HTTPException
import logging
import os
import uuid
from pathlib import Path

from ..models.video import Video, VideoResponse, VideoMetrics, VideoThumbnail, VideoCategory, VideoStatus
from ..models.user import User
from ..repositories.video_repository import video_repository
from ..repositories.user_repository import user_repository
from ..core.cache import get_cache

logger = logging.getLogger(__name__)

class UploadService:
    """
    MODULAR SERVICE: Video Upload Management
    Handles video uploads, file processing, and metadata management
    Following modular monolith principles with clear boundaries
    """
    
    def __init__(self):
        self.video_repo = video_repository
        self.user_repo = user_repository
        self.upload_dir = Path("/app/uploads")
        self.thumbnail_dir = Path("/app/uploads/thumbnails")
        self.max_file_size = 500 * 1024 * 1024  # 500MB
        self.allowed_formats = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        
        # Create upload directories
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
    
    async def upload_video(
        self,
        user_id: str,
        video_file: UploadFile,
        title: str,
        description: str = "",
        category: VideoCategory = VideoCategory.ENTERTAINMENT,
        tags: List[str] = None,
        thumbnail_file: Optional[UploadFile] = None
    ) -> Optional[VideoResponse]:
        """
        Upload and process a new video
        Core business logic for video upload workflow
        """
        try:
            # Validate user permissions
            user = await self.user_repo.get_by_id(user_id)
            if not user or not user.can_upload_videos():
                logger.warning(f"User {user_id} cannot upload videos")
                raise HTTPException(status_code=403, detail="User not authorized to upload videos")
            
            # Validate file
            await self._validate_video_file(video_file)
            
            # Generate unique file names
            video_id = str(uuid.uuid4())
            file_extension = Path(video_file.filename).suffix.lower()
            video_filename = f"{video_id}{file_extension}"
            video_path = self.upload_dir / video_filename
            
            # Save video file
            await self._save_uploaded_file(video_file, video_path)
            
            # Process thumbnail
            thumbnail_url = None
            if thumbnail_file:
                thumbnail_path = await self._process_thumbnail(video_id, thumbnail_file)
                thumbnail_url = f"/uploads/thumbnails/{thumbnail_path.name}"
            else:
                # Auto-generate thumbnail from video (placeholder for now)
                thumbnail_url = "/assets/default-thumbnail.jpg"
            
            # Get video metadata (duration, resolution, etc.)
            video_metadata = await self._extract_video_metadata(video_path)
            
            # Create video document
            thumbnails = [VideoThumbnail(
                url=thumbnail_url,
                width=1280,
                height=720
            )] if thumbnail_url else []
            
            video = Video(
                title=title,
                description=description,
                channel_id=user.channel_id or user.id,
                channel_name=user.channel_name or user.username,
                channel_avatar=user.avatar_url,
                video_url=f"/uploads/{video_filename}",
                youtube_embed_url=None,  # Local video, not YouTube
                duration_seconds=video_metadata.get('duration', 0),
                thumbnails=thumbnails,
                category=category,
                tags=tags or [],
                status=VideoStatus.PUBLISHED,  # Can be DRAFT initially
                metrics=VideoMetrics()
            )
            
            # Save to database
            created_video = await self.video_repo.create(video)
            
            # Update user stats
            await self.user_repo.update_by_id(user_id, {
                "$inc": {"stats.videos_uploaded": 1},
                "$set": {"stats.last_video_upload": datetime.utcnow()}
            })
            
            # Clear cache
            cache = await get_cache()
            if cache:
                await cache.delete_pattern("trending_videos:*")
                await cache.delete_pattern("videos_by_category:*")
            
            logger.info(f"Video uploaded successfully: {created_video.id} by user {user_id}")
            return VideoResponse.from_video(created_video)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            # Clean up uploaded file on error
            if video_path.exists():
                video_path.unlink()
            raise HTTPException(status_code=500, detail="Failed to upload video")
    
    async def _validate_video_file(self, video_file: UploadFile):
        """Validate uploaded video file"""
        if not video_file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        file_extension = Path(video_file.filename).suffix.lower()
        if file_extension not in self.allowed_formats:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file format. Allowed: {', '.join(self.allowed_formats)}"
            )
        
        # Reset file position to get accurate size
        await video_file.seek(0)
        content = await video_file.read()
        if len(content) > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {self.max_file_size // (1024*1024)}MB"
            )
        
        # Reset file position for actual saving
        await video_file.seek(0)
    
    async def _save_uploaded_file(self, upload_file: UploadFile, file_path: Path):
        """Save uploaded file to disk"""
        try:
            with open(file_path, "wb") as f:
                content = await upload_file.read()
                f.write(content)
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {e}")
            raise HTTPException(status_code=500, detail="Failed to save uploaded file")
    
    async def _process_thumbnail(self, video_id: str, thumbnail_file: UploadFile) -> Path:
        """Process and save thumbnail file"""
        file_extension = Path(thumbnail_file.filename).suffix.lower()
        if file_extension not in {'.jpg', '.jpeg', '.png', '.webp'}:
            raise HTTPException(status_code=400, detail="Invalid thumbnail format")
        
        thumbnail_filename = f"{video_id}_thumb{file_extension}"
        thumbnail_path = self.thumbnail_dir / thumbnail_filename
        
        await self._save_uploaded_file(thumbnail_file, thumbnail_path)
        return thumbnail_path
    
    async def _extract_video_metadata(self, video_path: Path) -> Dict[str, Any]:
        """Extract video metadata (duration, resolution, etc.)"""
        # Placeholder implementation
        # In production, use ffmpeg or similar to extract metadata
        return {
            'duration': 300,  # Default 5 minutes
            'width': 1920,
            'height': 1080,
            'bitrate': 5000,
            'fps': 30
        }
    
    async def get_user_uploads(self, user_id: str, limit: int = 50, offset: int = 0) -> List[VideoResponse]:
        """Get videos uploaded by a specific user"""
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return []
            
            videos = await self.video_repo.get_by_channel(
                str(user.channel_id or user.id),
                limit=limit,
                offset=offset
            )
            
            return [VideoResponse.from_video(video) for video in videos]
            
        except Exception as e:
            logger.error(f"Error getting user uploads: {e}")
            return []
    
    async def delete_video(self, video_id: str, user_id: str) -> bool:
        """Delete a video (soft delete)"""
        try:
            video = await self.video_repo.get_by_id(video_id)
            if not video:
                return False
            
            user = await self.user_repo.get_by_id(user_id)
            if not user or str(video.channel_id) != str(user.channel_id or user.id):
                raise HTTPException(status_code=403, detail="Not authorized to delete this video")
            
            # Soft delete by changing status
            await self.video_repo.update_by_id(video_id, {"status": VideoStatus.REMOVED})
            
            # Update user stats
            await self.user_repo.update_by_id(user_id, {
                "$inc": {"stats.videos_uploaded": -1}
            })
            
            logger.info(f"Video deleted: {video_id} by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting video: {e}")
            return False


# Global service instance following modular monolith pattern
upload_service = UploadService()