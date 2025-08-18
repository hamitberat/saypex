from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import secrets
import hashlib
import httpx
from fastapi import HTTPException

from ..models.user import User, UserRole, UserStatus, UserStats, UserPreferences
from ..repositories.user_repository import user_repository
from ..core.security import create_access_token
from ..services.user_service import user_service

logger = logging.getLogger(__name__)

class OAuthService:
    """
    MODULAR SERVICE: OAuth Integration
    Handles Google and Facebook OAuth authentication
    Following modular monolith principles with clear separation of concerns
    """
    
    def __init__(self):
        self.user_repo = user_repository
        self.oauth_providers = {
            'google': {
                'client_id': 'YOUR_GOOGLE_CLIENT_ID',  # To be configured
                'client_secret': 'YOUR_GOOGLE_CLIENT_SECRET',  # To be configured
                'auth_url': 'https://accounts.google.com/o/oauth2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'user_info_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
                'scope': 'openid email profile'
            },
            'facebook': {
                'client_id': 'YOUR_FACEBOOK_APP_ID',  # To be configured
                'client_secret': 'YOUR_FACEBOOK_APP_SECRET',  # To be configured
                'auth_url': 'https://www.facebook.com/v18.0/dialog/oauth',
                'token_url': 'https://graph.facebook.com/v18.0/oauth/access_token',
                'user_info_url': 'https://graph.facebook.com/v18.0/me',
                'scope': 'email'
            }
        }
        
        # OAuth state storage (in production, use Redis or database)
        self._oauth_states: Dict[str, Dict[str, Any]] = {}
    
    def generate_oauth_url(self, provider: str, redirect_uri: str) -> str:
        """
        Generate OAuth authorization URL
        Creates secure state parameter for CSRF protection
        """
        if provider not in self.oauth_providers:
            raise HTTPException(status_code=400, detail=f"Unsupported OAuth provider: {provider}")
        
        config = self.oauth_providers[provider]
        
        # Generate secure state parameter
        state = secrets.token_urlsafe(32)
        self._oauth_states[state] = {
            'provider': provider,
            'redirect_uri': redirect_uri,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(minutes=10)
        }
        
        # Build authorization URL
        params = {
            'client_id': config['client_id'],
            'redirect_uri': redirect_uri,
            'scope': config['scope'],
            'response_type': 'code',
            'state': state
        }
        
        query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
        return f"{config['auth_url']}?{query_string}"
    
    async def handle_oauth_callback(
        self, 
        provider: str, 
        code: str, 
        state: str, 
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Handle OAuth callback and create/login user
        Complete OAuth flow with token exchange and user creation
        """
        try:
            # Validate state parameter
            if state not in self._oauth_states:
                raise HTTPException(status_code=400, detail="Invalid OAuth state")
            
            state_data = self._oauth_states[state]
            if state_data['provider'] != provider:
                raise HTTPException(status_code=400, detail="OAuth provider mismatch")
            
            if datetime.utcnow() > state_data['expires_at']:
                raise HTTPException(status_code=400, detail="OAuth state expired")
            
            # Clean up state
            del self._oauth_states[state]
            
            # Exchange code for access token
            token_data = await self._exchange_code_for_token(provider, code, redirect_uri)
            
            # Get user info from provider
            user_info = await self._get_user_info(provider, token_data['access_token'])
            
            # Find or create user
            user = await self._find_or_create_oauth_user(provider, user_info)
            
            # Generate our own access token
            access_token = create_access_token(data={"sub": str(user.id)})
            
            return {
                'access_token': access_token,
                'token_type': 'bearer',
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'avatar_url': user.avatar_url,
                    'role': user.role,
                    'status': user.status,
                    'is_verified': user.is_verified,
                    'channel_id': str(user.channel_id) if user.channel_id else None,
                    'channel_name': user.channel_name,
                    'stats': user.stats,
                    'created_at': user.created_at
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error handling OAuth callback: {e}")
            raise HTTPException(status_code=500, detail="OAuth authentication failed")
    
    async def _exchange_code_for_token(self, provider: str, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        config = self.oauth_providers[provider]
        
        token_data = {
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(config['token_url'], data=token_data)
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.text}")
                raise HTTPException(status_code=400, detail="Failed to exchange OAuth code")
            
            return response.json()
    
    async def _get_user_info(self, provider: str, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth provider"""
        config = self.oauth_providers[provider]
        
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {}
        
        # Facebook requires fields parameter
        if provider == 'facebook':
            params['fields'] = 'id,email,name,picture'
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                config['user_info_url'],
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get user info: {response.text}")
                raise HTTPException(status_code=400, detail="Failed to get user information")
            
            return response.json()
    
    async def _find_or_create_oauth_user(self, provider: str, user_info: Dict[str, Any]) -> User:
        """Find existing user or create new one from OAuth data"""
        # Extract email from provider-specific response
        email = self._extract_email(provider, user_info)
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")
        
        # Check if user exists
        existing_user = await self.user_repo.find_one({'email': email.lower()})
        if existing_user:
            # Update OAuth provider info if needed
            await self._update_oauth_info(existing_user, provider, user_info)
            return existing_user
        
        # Create new user
        username = self._generate_username(provider, user_info, email)
        full_name = self._extract_full_name(provider, user_info)
        avatar_url = self._extract_avatar_url(provider, user_info)
        
        # Generate a placeholder password hash (user won't use it for OAuth login)
        password_hash = user_service.hash_password(secrets.token_urlsafe(32))
        
        user = User(
            username=username,
            email=email.lower(),
            full_name=full_name,
            password_hash=password_hash,
            avatar_url=avatar_url,
            role=UserRole.VIEWER,
            status=UserStatus.ACTIVE,
            is_email_verified=True,  # OAuth providers verify email
            stats=UserStats(),
            preferences=UserPreferences(),
            # Store OAuth provider info
            oauth_providers=[provider]
        )
        
        created_user = await self.user_repo.create(user)
        logger.info(f"Created new OAuth user: {username} via {provider}")
        
        return created_user
    
    def _extract_email(self, provider: str, user_info: Dict[str, Any]) -> Optional[str]:
        """Extract email from provider-specific user info"""
        return user_info.get('email')
    
    def _extract_full_name(self, provider: str, user_info: Dict[str, Any]) -> Optional[str]:
        """Extract full name from provider-specific user info"""
        if provider == 'google':
            return user_info.get('name')
        elif provider == 'facebook':
            return user_info.get('name')
        return None
    
    def _extract_avatar_url(self, provider: str, user_info: Dict[str, Any]) -> Optional[str]:
        """Extract avatar URL from provider-specific user info"""
        if provider == 'google':
            return user_info.get('picture')
        elif provider == 'facebook':
            picture_data = user_info.get('picture', {})
            if isinstance(picture_data, dict):
                return picture_data.get('data', {}).get('url')
        return None
    
    def _generate_username(self, provider: str, user_info: Dict[str, Any], email: str) -> str:
        """Generate unique username from OAuth data"""
        # Try to use name first
        if provider == 'google':
            base_name = user_info.get('name', '').replace(' ', '').lower()
        elif provider == 'facebook':
            base_name = user_info.get('name', '').replace(' ', '').lower()
        else:
            base_name = email.split('@')[0]
        
        # Remove special characters
        base_name = ''.join(c for c in base_name if c.isalnum())
        
        # Ensure username is valid
        if not base_name or len(base_name) < 3:
            base_name = f"{provider}_user"
        
        # Add provider prefix to avoid conflicts
        username = f"{provider}_{base_name}"
        
        # Truncate if too long
        if len(username) > 25:
            username = username[:25]
        
        return username
    
    async def _update_oauth_info(self, user: User, provider: str, user_info: Dict[str, Any]):
        """Update existing user with OAuth provider information"""
        updates = {}
        
        # Update avatar if user doesn't have one
        if not user.avatar_url:
            avatar_url = self._extract_avatar_url(provider, user_info)
            if avatar_url:
                updates['avatar_url'] = avatar_url
        
        # Update full name if user doesn't have one
        if not user.full_name:
            full_name = self._extract_full_name(provider, user_info)
            if full_name:
                updates['full_name'] = full_name
        
        # Add OAuth provider to list
        oauth_providers = getattr(user, 'oauth_providers', [])
        if provider not in oauth_providers:
            oauth_providers.append(provider)
            updates['oauth_providers'] = oauth_providers
        
        if updates:
            await self.user_repo.update_by_id(str(user.id), updates)
    
    def cleanup_expired_states(self):
        """Clean up expired OAuth states (should be called periodically)"""
        current_time = datetime.utcnow()
        expired_states = [
            state for state, data in self._oauth_states.items()
            if current_time > data['expires_at']
        ]
        
        for state in expired_states:
            del self._oauth_states[state]
        
        if expired_states:
            logger.info(f"Cleaned up {len(expired_states)} expired OAuth states")


# Global service instance following modular monolith pattern
oauth_service = OAuthService()