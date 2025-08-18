from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import secrets
import pyotp
import qrcode
import io
import base64
from fastapi import HTTPException

from ..models.user import User
from ..repositories.user_repository import user_repository
from ..core.security import create_access_token

logger = logging.getLogger(__name__)

class TFAService:
    """
    MODULAR SERVICE: Two-Factor Authentication
    Handles TOTP (Time-based One-Time Password) and backup codes
    Following modular monolith principles with clear security boundaries
    """
    
    def __init__(self):
        self.user_repo = user_repository
        self.issuer_name = "SAYPEX"
        # Backup codes storage (in production, store encrypted in database)
        self._backup_codes: Dict[str, list] = {}
    
    async def setup_totp(self, user_id: str) -> Dict[str, Any]:
        """
        Set up TOTP 2FA for user
        Generates secret key and QR code for authenticator apps
        """
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Generate secret key
            secret = pyotp.random_base32()
            
            # Create TOTP instance
            totp = pyotp.TOTP(secret)
            
            # Generate QR code URL for authenticator apps
            qr_url = totp.provisioning_uri(
                name=user.email,
                issuer_name=self.issuer_name
            )
            
            # Generate QR code image
            qr_code_image = self._generate_qr_code(qr_url)
            
            # Generate backup codes
            backup_codes = self._generate_backup_codes()
            
            # Store 2FA setup temporarily (not enabled until verified)
            await self.user_repo.update_by_id(user_id, {
                'tfa_secret': secret,
                'tfa_enabled': False,  # Not enabled until verified
                'tfa_setup_at': datetime.utcnow()
            })
            
            # Store backup codes temporarily
            self._backup_codes[user_id] = backup_codes
            
            logger.info(f"2FA setup initiated for user: {user_id}")
            
            return {
                'secret': secret,
                'qr_code_url': qr_url,
                'qr_code_image': qr_code_image,
                'backup_codes': backup_codes,
                'manual_entry_key': secret,
                'issuer': self.issuer_name,
                'account': user.email,
                'message': 'Scan QR code with your authenticator app, then verify with a code'
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error setting up TOTP: {e}")
            raise HTTPException(status_code=500, detail="Failed to setup 2FA")
    
    async def verify_totp_setup(self, user_id: str, totp_code: str) -> bool:
        """
        Verify TOTP setup and enable 2FA
        User must provide a valid TOTP code to complete setup
        """
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get temporary secret
            tfa_secret = getattr(user, 'tfa_secret', None)
            if not tfa_secret:
                raise HTTPException(status_code=400, detail="2FA setup not found. Please start setup again.")
            
            # Verify TOTP code
            totp = pyotp.TOTP(tfa_secret)
            if not totp.verify(totp_code, valid_window=1):
                raise HTTPException(status_code=400, detail="Invalid 2FA code")
            
            # Enable 2FA
            await self.user_repo.update_by_id(user_id, {
                'tfa_enabled': True,
                'tfa_verified_at': datetime.utcnow()
            })
            
            # Save backup codes permanently
            if user_id in self._backup_codes:
                await self.user_repo.update_by_id(user_id, {
                    'tfa_backup_codes': self._backup_codes[user_id]
                })
                del self._backup_codes[user_id]  # Remove from temporary storage
            
            logger.info(f"2FA enabled for user: {user_id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying TOTP setup: {e}")
            raise HTTPException(status_code=500, detail="Failed to verify 2FA setup")
    
    async def verify_totp_login(self, user_id: str, totp_code: str) -> bool:
        """
        Verify TOTP code during login
        Returns True if code is valid (TOTP or backup code)
        """
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return False
            
            # Check if 2FA is enabled
            tfa_enabled = getattr(user, 'tfa_enabled', False)
            tfa_secret = getattr(user, 'tfa_secret', None)
            
            if not tfa_enabled or not tfa_secret:
                return False
            
            # First try TOTP verification
            totp = pyotp.TOTP(tfa_secret)
            if totp.verify(totp_code, valid_window=1):
                logger.info(f"2FA login successful with TOTP for user: {user_id}")
                return True
            
            # If TOTP fails, try backup codes
            backup_codes = getattr(user, 'tfa_backup_codes', [])
            if totp_code in backup_codes:
                # Remove used backup code
                backup_codes.remove(totp_code)
                await self.user_repo.update_by_id(user_id, {
                    'tfa_backup_codes': backup_codes
                })
                logger.info(f"2FA login successful with backup code for user: {user_id}")
                return True
            
            logger.warning(f"Invalid 2FA code for user: {user_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error verifying TOTP login: {e}")
            return False
    
    async def disable_totp(self, user_id: str, password: str) -> bool:
        """
        Disable 2FA for user (requires password confirmation)
        """
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Verify password (import user_service to avoid circular import)
            from ..services.user_service import user_service
            if not user_service.verify_password(password, user.password_hash):
                raise HTTPException(status_code=400, detail="Invalid password")
            
            # Disable 2FA
            await self.user_repo.update_by_id(user_id, {
                'tfa_enabled': False,
                'tfa_secret': None,
                'tfa_backup_codes': [],
                'tfa_disabled_at': datetime.utcnow()
            })
            
            # Clean up temporary storage
            if user_id in self._backup_codes:
                del self._backup_codes[user_id]
            
            logger.info(f"2FA disabled for user: {user_id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error disabling TOTP: {e}")
            raise HTTPException(status_code=500, detail="Failed to disable 2FA")
    
    async def generate_new_backup_codes(self, user_id: str) -> list:
        """
        Generate new backup codes (invalidates old ones)
        """
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            tfa_enabled = getattr(user, 'tfa_enabled', False)
            if not tfa_enabled:
                raise HTTPException(status_code=400, detail="2FA not enabled")
            
            # Generate new backup codes
            backup_codes = self._generate_backup_codes()
            
            # Save new backup codes
            await self.user_repo.update_by_id(user_id, {
                'tfa_backup_codes': backup_codes,
                'tfa_backup_codes_generated_at': datetime.utcnow()
            })
            
            logger.info(f"New backup codes generated for user: {user_id}")
            return backup_codes
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating backup codes: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate backup codes")
    
    async def get_tfa_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get 2FA status for user
        """
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            tfa_enabled = getattr(user, 'tfa_enabled', False)
            tfa_setup_at = getattr(user, 'tfa_setup_at', None)
            tfa_verified_at = getattr(user, 'tfa_verified_at', None)
            backup_codes_count = len(getattr(user, 'tfa_backup_codes', []))
            
            return {
                'enabled': tfa_enabled,
                'setup_date': tfa_setup_at,
                'verified_date': tfa_verified_at,
                'backup_codes_remaining': backup_codes_count,
                'backup_codes_available': backup_codes_count > 0
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting 2FA status: {e}")
            raise HTTPException(status_code=500, detail="Failed to get 2FA status")
    
    def _generate_qr_code(self, data: str) -> str:
        """Generate QR code image as base64 string"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def _generate_backup_codes(self, count: int = 10) -> list:
        """Generate backup codes for 2FA"""
        backup_codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric backup codes
            code = ''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(8))
            backup_codes.append(code)
        return backup_codes


# Global service instance following modular monolith pattern
tfa_service = TFAService()