from typing import Optional, List
from datetime import datetime, timedelta
import logging
import secrets
import hashlib
from passlib.context import CryptContext
import jwt

from ..models.user import (
    User, UserResponse, PublicUserResponse, UserCreateRequest, 
    UserLoginRequest, UserUpdateRequest, UserRole, UserStatus
)
from ..repositories.user_repository import user_repository
from ..core.cache import get_cache
import os

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class UserService:
    """Enterprise user service with authentication and authorization"""
    
    def __init__(self):
        self.user_repo = user_repository
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None
    
    async def create_user(self, user_data: UserCreateRequest) -> Optional[UserResponse]:
        """Create a new user account"""
        try:
            # Check if user already exists
            existing_user = await self.user_repo.get_by_email(user_data.email)
            if existing_user:
                logger.warning(f"User registration failed - email already exists: {user_data.email}")
                return None
            
            existing_username = await self.user_repo.get_by_username(user_data.username)
            if existing_username:
                logger.warning(f"User registration failed - username already exists: {user_data.username}")
                return None
            
            # Hash password
            password_hash = self.hash_password(user_data.password)
            
            # Create user
            user = await self.user_repo.create_user(
                username=user_data.username,
                email=user_data.email,
                password_hash=password_hash,
                full_name=user_data.full_name,
                role=UserRole.VIEWER
            )
            
            # Generate email verification token
            verification_token = secrets.token_urlsafe(32)
            await self.user_repo.update_by_id(
                str(user.id),
                {"email_verification_token": verification_token}
            )
            
            logger.info(f"User created successfully: {user.id}")
            return UserResponse.from_user(user)
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def authenticate_user(self, login_data: UserLoginRequest) -> Optional[dict]:
        """Authenticate user and return token data"""
        try:
            # Get user by email
            user = await self.user_repo.get_by_email(login_data.email)
            if not user:
                logger.warning(f"Login failed - user not found: {login_data.email}")
                return None
            
            # Verify password
            if not self.verify_password(login_data.password, user.password_hash):
                logger.warning(f"Login failed - invalid password: {login_data.email}")
                return None
            
            # Check user status
            if user.status != UserStatus.ACTIVE:
                logger.warning(f"Login failed - user not active: {login_data.email}")
                return None
            
            # Update last login
            await self.user_repo.update_last_login(str(user.id))
            
            # Create access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={"sub": str(user.id), "username": user.username, "role": user.role},
                expires_delta=access_token_expires
            )
            
            logger.info(f"User authenticated successfully: {user.id}")
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": UserResponse.from_user(user)
            }
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    async def get_user(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        try:
            user = await self.user_repo.get_by_id(user_id)
            if user:
                return UserResponse.from_user(user)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def get_user_by_token(self, token: str) -> Optional[UserResponse]:
        """Get user from JWT token"""
        try:
            payload = self.verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            return await self.get_user(user_id)
            
        except Exception as e:
            logger.error(f"Error getting user by token: {e}")
            return None
    
    async def update_user(
        self, 
        user_id: str, 
        update_data: UserUpdateRequest
    ) -> Optional[UserResponse]:
        """Update user profile"""
        try:
            # Prepare update data
            update_dict = {}
            if update_data.username is not None:
                # Check if username is available
                existing = await self.user_repo.get_by_username(update_data.username)
                if existing and str(existing.id) != user_id:
                    logger.warning(f"Username already taken: {update_data.username}")
                    return None
                update_dict["username"] = update_data.username
            
            if update_data.full_name is not None:
                update_dict["full_name"] = update_data.full_name
            if update_data.bio is not None:
                update_dict["bio"] = update_data.bio
            if update_data.avatar_url is not None:
                update_dict["avatar_url"] = update_data.avatar_url
            if update_data.country is not None:
                update_dict["country"] = update_data.country
            if update_data.timezone is not None:
                update_dict["timezone"] = update_data.timezone
            if update_data.preferences is not None:
                update_dict["preferences"] = update_data.preferences.dict()
            
            # Update user
            updated_user = await self.user_repo.update_by_id(user_id, update_dict)
            if not updated_user:
                return None
            
            # Clear cache
            cache = await get_cache()
            await cache.delete(f"user_by_id:{user_id}")
            
            logger.info(f"User updated successfully: {user_id}")
            return UserResponse.from_user(updated_user)
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None
    
    async def create_channel(
        self, 
        user_id: str, 
        channel_name: str, 
        channel_description: Optional[str] = None
    ) -> Optional[UserResponse]:
        """Create a channel for user"""
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return None
            
            if user.channel_id:
                logger.warning(f"User {user_id} already has a channel")
                return None
            
            # Create channel
            updated_user = await self.user_repo.create_channel(
                user_id, channel_name, channel_description
            )
            
            if updated_user:
                logger.info(f"Channel created for user {user_id}: {channel_name}")
                return UserResponse.from_user(updated_user)
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating channel for user {user_id}: {e}")
            return None
    
    async def subscribe_to_channel(
        self, 
        subscriber_id: str, 
        channel_id: str
    ) -> bool:
        """Subscribe user to a channel"""
        try:
            # Check if channel exists
            channel_owner = await self.user_repo.get_by_field("channel_id", channel_id)
            if not channel_owner:
                logger.warning(f"Channel not found: {channel_id}")
                return False
            
            # Check if already subscribed
            is_subscribed = await self.user_repo.is_subscribed(subscriber_id, channel_id)
            if is_subscribed:
                logger.warning(f"User {subscriber_id} already subscribed to {channel_id}")
                return False
            
            # Subscribe
            success = await self.user_repo.subscribe_to_channel(subscriber_id, channel_id)
            
            if success:
                logger.info(f"User {subscriber_id} subscribed to channel {channel_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error subscribing user {subscriber_id} to channel {channel_id}: {e}")
            return False
    
    async def unsubscribe_from_channel(
        self, 
        subscriber_id: str, 
        channel_id: str
    ) -> bool:
        """Unsubscribe user from a channel"""
        try:
            success = await self.user_repo.unsubscribe_from_channel(subscriber_id, channel_id)
            
            if success:
                logger.info(f"User {subscriber_id} unsubscribed from channel {channel_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error unsubscribing user {subscriber_id} from channel {channel_id}: {e}")
            return False
    
    async def get_subscriptions(self, user_id: str) -> List[PublicUserResponse]:
        """Get user's subscriptions"""
        try:
            subscriptions = await self.user_repo.get_subscriptions(user_id)
            return [PublicUserResponse.from_user(user) for user in subscriptions]
            
        except Exception as e:
            logger.error(f"Error getting subscriptions for user {user_id}: {e}")
            return []
    
    async def search_users(self, query: str, limit: int = 20) -> List[PublicUserResponse]:
        """Search users and channels"""
        try:
            users = await self.user_repo.search_users(query, limit)
            return [PublicUserResponse.from_user(user) for user in users]
            
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []
    
    async def get_public_user(self, user_id: str) -> Optional[PublicUserResponse]:
        """Get public user profile"""
        try:
            user = await self.user_repo.get_by_id(user_id)
            if user:
                return PublicUserResponse.from_user(user)
            return None
            
        except Exception as e:
            logger.error(f"Error getting public user {user_id}: {e}")
            return None
    
    async def change_password(
        self, 
        user_id: str, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """Change user password"""
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return False
            
            # Verify current password
            if not self.verify_password(current_password, user.password_hash):
                logger.warning(f"Password change failed - invalid current password: {user_id}")
                return False
            
            # Hash new password
            new_password_hash = self.hash_password(new_password)
            
            # Update password
            success = await self.user_repo.update_password(user_id, new_password_hash)
            
            if success:
                logger.info(f"Password changed successfully: {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error changing password for user {user_id}: {e}")
            return False
    
    async def verify_email(self, user_id: str, verification_token: str) -> bool:
        """Verify user email"""
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return False
            
            if user.is_email_verified:
                return True
            
            if user.email_verification_token != verification_token:
                logger.warning(f"Email verification failed - invalid token: {user_id}")
                return False
            
            # Verify email
            success = await self.user_repo.verify_email(user_id)
            
            if success:
                logger.info(f"Email verified successfully: {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error verifying email for user {user_id}: {e}")
            return False


# Global service instance
user_service = UserService()