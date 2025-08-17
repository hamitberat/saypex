from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from ..services.user_service import user_service
from ..models.user import UserResponse, UserRole

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserResponse]:
    """Get current authenticated user from JWT token"""
    if not credentials:
        return None
    
    try:
        user = await user_service.get_user_by_token(credentials.credentials)
        return user
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return None


async def require_auth(
    current_user: Optional[UserResponse] = Depends(get_current_user)
) -> UserResponse:
    """Require authentication - raises HTTPException if not authenticated"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def require_creator(
    current_user: UserResponse = Depends(require_auth)
) -> UserResponse:
    """Require creator role or higher"""
    if current_user.role not in [UserRole.CREATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Creator role required"
        )
    return current_user


async def require_admin(
    current_user: UserResponse = Depends(require_auth)
) -> UserResponse:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return current_user


async def require_moderator(
    current_user: UserResponse = Depends(require_auth)
) -> UserResponse:
    """Require moderator role or higher"""
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator role required"
        )
    return current_user


def optional_auth():
    """Optional authentication - returns None if not authenticated"""
    return Depends(get_current_user)