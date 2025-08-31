"""
PostgreSQL User Repository
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid

from database.models import User, UserRole, UserStatus
from models.user import UserCreateRequest, UserUpdateRequest, UserPreferences, UserStats


class PostgreSQLUserRepository:
    """PostgreSQL implementation of User Repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_user(self, user_data: UserCreateRequest, password_hash: str) -> User:
        """Create a new user"""
        try:
            # Create default preferences and stats
            default_preferences = {
                "language": "en",
                "theme": "light",
                "autoplay": True,
                "notifications_enabled": True,
                "email_notifications": True,
                "content_filter": "moderate",
                "preferred_quality": "auto",
                "show_subscriptions": True,
                "show_playlists": True,
                "show_liked_videos": False
            }
            
            default_stats = {
                "total_watch_time_minutes": 0.0,
                "videos_watched": 0,
                "subscriptions_count": 0,
                "subscribers_count": 0,
                "videos_uploaded": 0,
                "total_video_views": 0,
                "likes_given": 0,
                "comments_made": 0,
                "last_active": None,
                "last_video_upload": None
            }
            
            db_user = User(
                username=user_data.username.lower(),
                email=user_data.email.lower(),
                full_name=user_data.full_name,
                password_hash=password_hash,
                date_of_birth=user_data.date_of_birth,
                country=user_data.country,
                preferences=default_preferences,
                stats=default_stats,
                oauth_providers=[],
                tfa_backup_codes=[]
            )
            
            self.session.add(db_user)
            await self.session.flush()  # Get the ID without committing
            return db_user
            
        except IntegrityError as e:
            await self.session.rollback()
            if "username" in str(e.orig):
                raise ValueError("Username already exists")
            elif "email" in str(e.orig):
                raise ValueError("Email already exists")
            else:
                raise ValueError("User creation failed")
    
    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        stmt = select(User).where(User.email == email.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        stmt = select(User).where(User.username == username.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: uuid.UUID, user_data: UserUpdateRequest) -> Optional[User]:
        """Update user information"""
        try:
            update_data = {}
            
            if user_data.username:
                update_data['username'] = user_data.username.lower()
            if user_data.full_name is not None:
                update_data['full_name'] = user_data.full_name
            if user_data.bio is not None:
                update_data['bio'] = user_data.bio
            if user_data.avatar_url is not None:
                update_data['avatar_url'] = user_data.avatar_url
            if user_data.country is not None:
                update_data['country'] = user_data.country
            if user_data.timezone is not None:
                update_data['timezone'] = user_data.timezone
            if user_data.preferences is not None:
                update_data['preferences'] = user_data.preferences.dict()
            
            if update_data:
                stmt = update(User).where(User.id == user_id).values(**update_data)
                await self.session.execute(stmt)
                
            return await self.get_user_by_id(user_id)
            
        except IntegrityError as e:
            await self.session.rollback()
            if "username" in str(e.orig):
                raise ValueError("Username already exists")
            else:
                raise ValueError("User update failed")
    
    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """Delete user (soft delete by changing status)"""
        stmt = update(User).where(User.id == user_id).values(status=UserStatus.BANNED)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def verify_email(self, user_id: uuid.UUID) -> bool:
        """Verify user email"""
        stmt = update(User).where(User.id == user_id).values(
            is_email_verified=True,
            email_verification_token=None
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def update_password(self, user_id: uuid.UUID, password_hash: str) -> bool:
        """Update user password"""
        stmt = update(User).where(User.id == user_id).values(
            password_hash=password_hash,
            password_reset_token=None,
            password_reset_expires=None
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def set_password_reset_token(self, user_id: uuid.UUID, token: str, expires_at) -> bool:
        """Set password reset token"""
        stmt = update(User).where(User.id == user_id).values(
            password_reset_token=token,
            password_reset_expires=expires_at
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def update_last_login(self, user_id: uuid.UUID) -> bool:
        """Update last login timestamp"""
        stmt = update(User).where(User.id == user_id).values(last_login=func.now())
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def search_users(self, query: str, limit: int = 20, offset: int = 0) -> List[User]:
        """Search users by username or full name"""
        search_term = f"%{query.lower()}%"
        stmt = select(User).where(
            and_(
                User.status == UserStatus.ACTIVE,
                or_(
                    User.username.ilike(search_term),
                    User.full_name.ilike(search_term)
                )
            )
        ).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_user_stats(self, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Get user statistics"""
        user = await self.get_user_by_id(user_id)
        return user.stats if user else None
    
    async def update_user_stats(self, user_id: uuid.UUID, stats_update: Dict[str, Any]) -> bool:
        """Update user statistics"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        current_stats = user.stats or {}
        
        # Update stats
        for key, value in stats_update.items():
            if key in ['total_watch_time_minutes', 'videos_watched', 'likes_given', 'comments_made']:
                # Increment counters
                current_stats[key] = current_stats.get(key, 0) + value
            else:
                current_stats[key] = value
        
        current_stats['last_active'] = func.now()
        
        stmt = update(User).where(User.id == user_id).values(stats=current_stats)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def get_users_by_role(self, role: UserRole, limit: int = 50, offset: int = 0) -> List[User]:
        """Get users by role"""
        stmt = select(User).where(
            and_(User.role == role, User.status == UserStatus.ACTIVE)
        ).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def count_users(self, status: Optional[UserStatus] = None) -> int:
        """Count users with optional status filter"""
        if status:
            stmt = select(func.count(User.id)).where(User.status == status)
        else:
            stmt = select(func.count(User.id))
        
        result = await self.session.execute(stmt)
        return result.scalar()
    
    # 2FA methods
    async def enable_2fa(self, user_id: uuid.UUID, secret: str, backup_codes: List[str]) -> bool:
        """Enable 2FA for user"""
        stmt = update(User).where(User.id == user_id).values(
            tfa_enabled=True,
            tfa_secret=secret,
            tfa_backup_codes=backup_codes,
            tfa_setup_at=func.now()
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def disable_2fa(self, user_id: uuid.UUID) -> bool:
        """Disable 2FA for user"""
        stmt = update(User).where(User.id == user_id).values(
            tfa_enabled=False,
            tfa_secret=None,
            tfa_backup_codes=[],
            tfa_disabled_at=func.now()
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def verify_2fa(self, user_id: uuid.UUID) -> bool:
        """Mark 2FA as verified"""
        stmt = update(User).where(User.id == user_id).values(tfa_verified_at=func.now())
        result = await self.session.execute(stmt)
        return result.rowcount > 0