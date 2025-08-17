from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..models.comment import (
    Comment, CommentResponse, CommentCreateRequest, CommentUpdateRequest,
    CommentTreeResponse, CommentModerationRequest, CommentStatus
)
from ..repositories.comment_repository import comment_repository
from ..repositories.user_repository import user_repository
from ..repositories.video_repository import video_repository
from ..core.cache import get_cache

logger = logging.getLogger(__name__)


class CommentService:
    """Enterprise comment service with threading and moderation"""
    
    def __init__(self):
        self.comment_repo = comment_repository
        self.user_repo = user_repository
        self.video_repo = video_repository
    
    async def create_comment(
        self, 
        comment_data: CommentCreateRequest, 
        author_id: str
    ) -> Optional[CommentResponse]:
        """Create a new comment with validation"""
        try:
            # Validate author
            author = await self.user_repo.get_by_id(author_id)
            if not author:
                logger.warning(f"Comment creation failed - author not found: {author_id}")
                return None
            
            # Validate video exists
            video = await self.video_repo.get_by_id(comment_data.video_id)
            if not video:
                logger.warning(f"Comment creation failed - video not found: {comment_data.video_id}")
                return None
            
            # Validate parent comment if replying
            if comment_data.parent_id:
                parent_comment = await self.comment_repo.get_by_id(comment_data.parent_id)
                if not parent_comment:
                    logger.warning(f"Comment creation failed - parent comment not found: {comment_data.parent_id}")
                    return None
                
                if not parent_comment.can_be_replied_to():
                    logger.warning(f"Comment creation failed - cannot reply to comment: {comment_data.parent_id}")
                    return None
            
            # Create comment
            comment = await self.comment_repo.create_comment(
                content=comment_data.content,
                video_id=comment_data.video_id,
                author_id=author_id,
                author_username=author.username,
                author_avatar=author.avatar_url,
                parent_id=comment_data.parent_id
            )
            
            # Update video comment count
            await self.video_repo.update_video_metrics(
                comment_data.video_id,
                {"comments_count": {"$inc": 1}}
            )
            
            # Update user stats
            await self.user_repo.update_user_stats(
                author_id,
                {"comments_made": {"$inc": 1}}
            )
            
            # Clear cache
            cache = await get_cache()
            await cache.delete_pattern(f"video_comments:{comment_data.video_id}:*")
            
            logger.info(f"Comment created: {comment.id} by {author_id}")
            return CommentResponse.from_comment(comment)
            
        except Exception as e:
            logger.error(f"Error creating comment: {e}")
            return None
    
    async def get_video_comments(
        self,
        video_id: str,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "created_at",
        include_replies: bool = True
    ) -> CommentTreeResponse:
        """Get comments for a video with optional replies"""
        try:
            # Get root comments
            comments = await self.comment_repo.get_video_comments(
                video_id=video_id,
                limit=limit,
                offset=offset,
                sort_by=sort_by
            )
            
            comment_responses = []
            
            for comment in comments:
                # Get replies if requested
                replies = []
                if include_replies and not comment.is_reply():
                    reply_comments = await self.comment_repo.get_comment_replies(
                        str(comment.id), limit=10
                    )
                    replies = [CommentResponse.from_comment(reply) for reply in reply_comments]
                
                comment_response = CommentResponse.from_comment(comment, replies)
                comment_responses.append(comment_response)
            
            # Get total count
            total_count = await self.comment_repo.count({
                "video_id": video_id,
                "parent_id": None,
                "status": CommentStatus.ACTIVE
            })
            
            has_more = (offset + limit) < total_count
            next_cursor = str(offset + limit) if has_more else None
            
            return CommentTreeResponse(
                comments=comment_responses,
                total_count=total_count,
                has_more=has_more,
                next_cursor=next_cursor
            )
            
        except Exception as e:
            logger.error(f"Error getting video comments: {e}")
            return CommentTreeResponse(comments=[], total_count=0, has_more=False)
    
    async def get_comment_replies(
        self,
        parent_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[CommentResponse]:
        """Get replies to a specific comment"""
        try:
            replies = await self.comment_repo.get_comment_replies(
                parent_id=parent_id,
                limit=limit,
                offset=offset
            )
            
            return [CommentResponse.from_comment(reply) for reply in replies]
            
        except Exception as e:
            logger.error(f"Error getting comment replies: {e}")
            return []
    
    async def update_comment(
        self,
        comment_id: str,
        update_data: CommentUpdateRequest,
        user_id: str
    ) -> Optional[CommentResponse]:
        """Update comment with ownership validation"""
        try:
            comment = await self.comment_repo.get_by_id(comment_id)
            if not comment:
                return None
            
            # Check ownership
            if str(comment.author_id) != user_id:
                logger.warning(f"User {user_id} cannot edit comment {comment_id}")
                return None
            
            # Update comment
            update_dict = {
                "content": update_data.content,
                "edited_at": datetime.utcnow()
            }
            
            updated_comment = await self.comment_repo.update_by_id(comment_id, update_dict)
            if not updated_comment:
                return None
            
            # Clear cache
            cache = await get_cache()
            await cache.delete_pattern(f"video_comments:{comment.video_id}:*")
            
            logger.info(f"Comment updated: {comment_id} by {user_id}")
            return CommentResponse.from_comment(updated_comment)
            
        except Exception as e:
            logger.error(f"Error updating comment {comment_id}: {e}")
            return None
    
    async def delete_comment(self, comment_id: str, user_id: str) -> bool:
        """Delete comment with ownership validation"""
        try:
            comment = await self.comment_repo.get_by_id(comment_id)
            if not comment:
                return False
            
            # Check ownership or admin privileges
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return False
            
            can_delete = (
                str(comment.author_id) == user_id or  # Comment author
                user.role in ["admin", "moderator"]  # Admin/moderator
            )
            
            if not can_delete:
                logger.warning(f"User {user_id} cannot delete comment {comment_id}")
                return False
            
            # Soft delete comment
            success = await self.comment_repo.moderate_comment(
                comment_id, "delete", user_id, "Deleted by user"
            )
            
            if success:
                # Update video comment count
                await self.video_repo.update_video_metrics(
                    str(comment.video_id),
                    {"comments_count": {"$inc": -1}}
                )
                
                # Clear cache
                cache = await get_cache()
                await cache.delete_pattern(f"video_comments:{comment.video_id}:*")
                
                logger.info(f"Comment deleted: {comment_id} by {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting comment {comment_id}: {e}")
            return False
    
    async def like_comment(self, comment_id: str, user_id: str) -> bool:
        """Like a comment"""
        try:
            success = await self.comment_repo.like_comment(comment_id, user_id)
            
            if success:
                # Update user stats
                await self.user_repo.update_user_stats(
                    user_id,
                    {"likes_given": {"$inc": 1}}
                )
                
                logger.info(f"Comment liked: {comment_id} by {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error liking comment {comment_id}: {e}")
            return False
    
    async def unlike_comment(self, comment_id: str, user_id: str) -> bool:
        """Remove like from comment"""
        try:
            success = await self.comment_repo.unlike_comment(comment_id, user_id)
            
            if success:
                logger.info(f"Comment unliked: {comment_id} by {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error unliking comment {comment_id}: {e}")
            return False
    
    async def moderate_comment(
        self,
        comment_id: str,
        moderation_data: CommentModerationRequest,
        moderator_id: str
    ) -> bool:
        """Moderate a comment (admin/moderator only)"""
        try:
            # Check moderator permissions
            moderator = await self.user_repo.get_by_id(moderator_id)
            if not moderator or moderator.role not in ["admin", "moderator"]:
                logger.warning(f"User {moderator_id} cannot moderate comments")
                return False
            
            success = await self.comment_repo.moderate_comment(
                comment_id,
                moderation_data.action,
                moderator_id,
                moderation_data.reason
            )
            
            if success:
                # Clear cache
                comment = await self.comment_repo.get_by_id(comment_id)
                if comment:
                    cache = await get_cache()
                    await cache.delete_pattern(f"video_comments:{comment.video_id}:*")
                
                logger.info(f"Comment moderated: {comment_id} by {moderator_id} - {moderation_data.action}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error moderating comment {comment_id}: {e}")
            return False
    
    async def pin_comment(self, comment_id: str, user_id: str) -> bool:
        """Pin a comment (channel owner only)"""
        try:
            comment = await self.comment_repo.get_by_id(comment_id)
            if not comment:
                return False
            
            # Check if user owns the video's channel
            video = await self.video_repo.get_by_id(str(comment.video_id))
            if not video:
                return False
            
            user = await self.user_repo.get_by_id(user_id)
            if not user or str(video.channel_id) != str(user.channel_id):
                logger.warning(f"User {user_id} cannot pin comment on video {video.id}")
                return False
            
            success = await self.comment_repo.pin_comment(comment_id)
            
            if success:
                logger.info(f"Comment pinned: {comment_id} by {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error pinning comment {comment_id}: {e}")
            return False
    
    async def heart_comment(self, comment_id: str, user_id: str) -> bool:
        """Heart a comment (channel owner only)"""
        try:
            comment = await self.comment_repo.get_by_id(comment_id)
            if not comment:
                return False
            
            # Check if user owns the video's channel
            video = await self.video_repo.get_by_id(str(comment.video_id))
            if not video:
                return False
            
            user = await self.user_repo.get_by_id(user_id)
            if not user or str(video.channel_id) != str(user.channel_id):
                logger.warning(f"User {user_id} cannot heart comment on video {video.id}")
                return False
            
            success = await self.comment_repo.heart_comment(comment_id)
            
            if success:
                logger.info(f"Comment hearted: {comment_id} by {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error hearting comment {comment_id}: {e}")
            return False
    
    async def flag_comment(self, comment_id: str, user_id: str) -> bool:
        """Flag a comment for review"""
        try:
            success = await self.comment_repo.flag_comment(comment_id, user_id)
            
            if success:
                logger.info(f"Comment flagged: {comment_id} by {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error flagging comment {comment_id}: {e}")
            return False
    
    async def get_user_comments(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[CommentResponse]:
        """Get comments by a specific user"""
        try:
            comments = await self.comment_repo.get_user_comments(
                author_id=user_id,
                limit=limit,
                offset=offset
            )
            
            return [CommentResponse.from_comment(comment) for comment in comments]
            
        except Exception as e:
            logger.error(f"Error getting user comments: {e}")
            return []


# Global service instance
comment_service = CommentService()