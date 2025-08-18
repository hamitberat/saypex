from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
from pydantic import BaseModel
import logging

from ..models.user import UserResponse
from ..services.tfa_service import tfa_service
from ..middleware.auth import require_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/2fa", tags=["2fa"])


class TFASetupResponse(BaseModel):
    """Response model for 2FA setup"""
    secret: str
    qr_code_url: str
    qr_code_image: str
    backup_codes: List[str]
    manual_entry_key: str
    issuer: str
    account: str
    message: str


class TFAVerifyRequest(BaseModel):
    """Request model for 2FA verification"""
    code: str


class TFADisableRequest(BaseModel):
    """Request model for disabling 2FA"""
    password: str


@router.post("/setup", response_model=TFASetupResponse)
async def setup_2fa(current_user: UserResponse = Depends(require_auth)):
    """
    Set up 2FA for current user
    MODULAR API ENDPOINT: Delegates to tfa_service for business logic
    """
    try:
        setup_data = await tfa_service.setup_totp(current_user.id)
        return TFASetupResponse(**setup_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in 2FA setup endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup 2FA"
        )


@router.post("/verify-setup")
async def verify_2fa_setup(
    verify_request: TFAVerifyRequest,
    current_user: UserResponse = Depends(require_auth)
):
    """
    Verify 2FA setup and enable 2FA
    """
    try:
        success = await tfa_service.verify_totp_setup(current_user.id, verify_request.code)
        
        if success:
            return {
                "message": "2FA enabled successfully",
                "enabled": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid 2FA code"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying 2FA setup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify 2FA setup"
        )


@router.post("/verify-login")
async def verify_2fa_login(verify_request: TFAVerifyRequest):
    """
    Verify 2FA code during login
    This endpoint is used by the login flow
    """
    try:
        # This endpoint would be called by the login process
        # For now, return method information
        return {
            "message": "2FA verification endpoint ready",
            "supported_methods": ["totp", "backup_codes"],
            "note": "This endpoint is used by the login process when 2FA is enabled"
        }
        
    except Exception as e:
        logger.error(f"Error in 2FA login verification endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify 2FA for login"
        )


@router.post("/disable")
async def disable_2fa(
    disable_request: TFADisableRequest,
    current_user: UserResponse = Depends(require_auth)
):
    """
    Disable 2FA for current user
    """
    try:
        success = await tfa_service.disable_totp(current_user.id, disable_request.password)
        
        if success:
            return {
                "message": "2FA disabled successfully",
                "enabled": False
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to disable 2FA"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling 2FA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable 2FA"
        )


@router.post("/backup-codes", response_model=List[str])
async def generate_backup_codes(current_user: UserResponse = Depends(require_auth)):
    """
    Generate new backup codes
    """
    try:
        backup_codes = await tfa_service.generate_new_backup_codes(current_user.id)
        return backup_codes
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating backup codes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate backup codes"
        )


@router.get("/status")
async def get_2fa_status(current_user: UserResponse = Depends(require_auth)):
    """
    Get 2FA status for current user
    """
    try:
        status_data = await tfa_service.get_tfa_status(current_user.id)
        return status_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting 2FA status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get 2FA status"
        )


@router.get("/info")
async def get_2fa_info():
    """
    Get general 2FA information
    """
    return {
        "supported_methods": [
            {
                "name": "totp",
                "display_name": "Time-based One-Time Password",
                "description": "Use authenticator apps like Google Authenticator, Authy, or Microsoft Authenticator",
                "apps": [
                    "Google Authenticator",
                    "Authy", 
                    "Microsoft Authenticator",
                    "1Password",
                    "Bitwarden"
                ]
            },
            {
                "name": "backup_codes",
                "display_name": "Backup Codes",
                "description": "Single-use codes for account recovery when you can't access your authenticator app",
                "count": 10
            }
        ],
        "issuer": "SAYPEX",
        "setup_required": True,
        "verification_window_seconds": 30
    }