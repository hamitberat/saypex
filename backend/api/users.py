from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
import logging

from ..models.user import (
    UserResponse, PublicUserResponse, UserCreateRequest, 
    UserLoginRequest, UserUpdateRequest
)
from ..services.user_service import user_service
from ..middleware.auth import require_auth, optional_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreateRequest):
    """Register a new user"""
    try:
        user = await user_service.create_user(user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user (email or username already exists)"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login")
async def login_user(login_data: UserLoginRequest):
    """Authenticate user and return access token"""
    try:
        auth_data = await user_service.authenticate_user(login_data)
        if not auth_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        return auth_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login user"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: UserResponse = Depends(require_auth)):
    """Get current user's profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    update_data: UserUpdateRequest,
    current_user: UserResponse = Depends(require_auth)
):
    """Update current user's profile"""
    try:
        user = await user_service.update_user(current_user.id, update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update user profile"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.get("/{user_id}", response_model=PublicUserResponse)
async def get_user_profile(user_id: str):
    """Get public user profile"""
    try:
        user = await user_service.get_public_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@router.post("/create-channel", response_model=UserResponse)
async def create_channel(
    channel_name: str,
    channel_description: Optional[str] = None,
    current_user: UserResponse = Depends(require_auth)
):
    """Create a channel for the current user"""
    try:
        user = await user_service.create_channel(
            current_user.id, channel_name, channel_description
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create channel (user already has a channel)"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating channel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create channel"
        )


@router.post("/subscribe/{channel_id}")
async def subscribe_to_channel(
    channel_id: str,
    current_user: UserResponse = Depends(require_auth)
):
    """Subscribe to a channel"""
    try:
        success = await user_service.subscribe_to_channel(current_user.id, channel_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to subscribe (channel not found or already subscribed)"
            )
        return {"message": "Subscribed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subscribing to channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to subscribe"
        )


@router.delete("/subscribe/{channel_id}")
async def unsubscribe_from_channel(
    channel_id: str,
    current_user: UserResponse = Depends(require_auth)
):
    """Unsubscribe from a channel"""
    try:
        success = await user_service.unsubscribe_from_channel(current_user.id, channel_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not subscribed to this channel"
            )
        return {"message": "Unsubscribed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unsubscribing from channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unsubscribe"
        )


@router.get("/me/subscriptions", response_model=List[PublicUserResponse])
async def get_user_subscriptions(current_user: UserResponse = Depends(require_auth)):
    """Get current user's subscriptions"""
    try:
        subscriptions = await user_service.get_subscriptions(current_user.id)
        return subscriptions
    except Exception as e:
        logger.error(f"Error getting user subscriptions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscriptions"
        )


@router.get("/search", response_model=List[PublicUserResponse])
async def search_users(
    q: str,
    limit: int = 20
):
    """Search users and channels"""
    try:
        users = await user_service.search_users(q, limit)
        return users
    except Exception as e:
        logger.error(f"Error searching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search users"
        )