from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
import logging

from ..services.oauth_service import oauth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.get("/{provider}/login")
async def oauth_login(
    provider: str,
    redirect_uri: str = Query(..., description="OAuth redirect URI")
):
    """
    Initiate OAuth login flow
    MODULAR API ENDPOINT: Delegates to oauth_service for business logic
    """
    try:
        if provider not in ['google', 'facebook']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported OAuth provider. Supported: google, facebook"
            )
        
        # Generate OAuth authorization URL
        auth_url = oauth_service.generate_oauth_url(provider, redirect_uri)
        
        return {
            'auth_url': auth_url,
            'provider': provider,
            'message': f'Redirect user to this URL to complete {provider} OAuth login'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating OAuth login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate OAuth login"
        )


@router.get("/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str = Query(..., description="OAuth authorization code"),
    state: str = Query(..., description="OAuth state parameter"),
    redirect_uri: str = Query(..., description="OAuth redirect URI")
):
    """
    Handle OAuth callback
    Complete OAuth authentication flow
    """
    try:
        if provider not in ['google', 'facebook']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported OAuth provider"
            )
        
        # Handle OAuth callback and create/login user
        auth_data = await oauth_service.handle_oauth_callback(
            provider=provider,
            code=code,
            state=state,
            redirect_uri=redirect_uri
        )
        
        return auth_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling OAuth callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth authentication failed"
        )


@router.get("/providers")
async def get_oauth_providers():
    """
    Get list of supported OAuth providers
    """
    return {
        'providers': [
            {
                'name': 'google',
                'display_name': 'Google',
                'icon': 'https://developers.google.com/identity/images/g-logo.png'
            },
            {
                'name': 'facebook',
                'display_name': 'Facebook',
                'icon': 'https://static.xx.fbcdn.net/rsrc.php/yb/r/hLRJ1GG_y0J.ico'
            }
        ],
        'redirect_uri_required': True,
        'state_expires_minutes': 10
    }


@router.post("/cleanup")
async def cleanup_expired_states():
    """
    Cleanup expired OAuth states (admin endpoint)
    """
    try:
        oauth_service.cleanup_expired_states()
        return {"message": "Expired OAuth states cleaned up successfully"}
        
    except Exception as e:
        logger.error(f"Error cleaning up OAuth states: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup OAuth states"
        )