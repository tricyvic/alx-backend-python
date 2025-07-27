from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from rest_framework import authentication, exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AnonymousUser
from typing import Optional, Tuple, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser as UserType
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using either
    their username or email address.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user by username or email
        """
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if username is None or password is None:
            return None
        
        try:
            # Try to get user by username first
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # If username doesn't exist, try email
                try:
                    user = User.objects.get(email=username)
                except User.DoesNotExist:
                    # Run the default password hasher once to reduce the timing
                    # difference between an existing and a nonexistent user (#20760).
                    User().set_password(password)
                    return None
        except User.MultipleObjectsReturned:
            # Multiple users with same email - this shouldn't happen if email is unique
            logger.warning(f"Multiple users found with identifier: {username}")
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            logger.info(f"User {user.username} authenticated successfully")
            return user
        
        return None


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that provides better error handling
    and logging for authentication attempts.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request and return a tuple of (user, token) if successful,
        or None if authentication fails.
        """
        try:
            result = super().authenticate(request)
            if result:
                user, validated_token = result
                logger.info(f"JWT authentication successful for user: {user.username}")
                return result
            return None
        except InvalidToken as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            raise exceptions.AuthenticationFailed(_('Invalid token.'))
        except TokenError as e:
            logger.warning(f"JWT token error: {str(e)}")
            raise exceptions.AuthenticationFailed(_('Token error.'))
        except Exception as e:
            logger.error(f"Unexpected JWT authentication error: {str(e)}")
            raise exceptions.AuthenticationFailed(_('Authentication failed.'))


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom API Key authentication for service-to-service communication.
    Add API keys to user profiles for this to work.
    """
    keyword = 'ApiKey'
    
    def authenticate(self, request):
        """
        Authenticate using API key in the Authorization header.
        Format: Authorization: ApiKey <api_key>
        """
        auth = authentication.get_authorization_header(request).split()
        
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None
        
        if len(auth) == 1:
            msg = _('Invalid API key header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid API key header. Credentials string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)
        
        try:
            api_key = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid API key header. Credentials string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)
        
        return self.authenticate_credentials(api_key)
    
    def authenticate_credentials(self, api_key):
        """
        Authenticate the API key and return the corresponding user.
        """
        try:
            # Assuming you have an api_key field in your User model
            # If not, you might need to create a separate APIKey model
            user = User.objects.get(api_key=api_key, is_active=True)
        except User.DoesNotExist:
            logger.warning(f"API key authentication failed for key: {api_key[:8]}...")
            raise exceptions.AuthenticationFailed(_('Invalid API key.'))
        except AttributeError:
            # If User model doesn't have api_key field
            logger.error("API key authentication requires api_key field in User model")
            raise exceptions.AuthenticationFailed(_('API key authentication not properly configured.'))
        
        logger.info(f"API key authentication successful for user: {user.username}")
        return (user, api_key)


class SessionOrTokenAuthentication(authentication.BaseAuthentication):
    """
    Composite authentication class that tries session authentication first,
    then falls back to JWT token authentication.
    """
    
    def authenticate(self, request):
        """
        Try session authentication first, then JWT token authentication.
        """
        # Try session authentication first
        session_auth = authentication.SessionAuthentication()
        try:
            result = session_auth.authenticate(request)
            if result:
                logger.info(f"Session authentication successful for user: {result[0].username}")
                return result
        except exceptions.AuthenticationFailed:
            pass  # Continue to JWT authentication
        
        # Try JWT authentication
        jwt_auth = CustomJWTAuthentication()
        try:
            result = jwt_auth.authenticate(request)
            if result:
                return result
        except exceptions.AuthenticationFailed:
            pass  # Authentication failed
        
        return None


class TokenService:
    """
    Service class for token-related operations
    """
    
    @staticmethod
    def generate_tokens_for_user(user) -> dict:
        """
        Generate access and refresh tokens for a user
        """
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'access_expires_in': refresh.access_token.lifetime.total_seconds() if refresh.access_token.lifetime is not None else 0,
            'refresh_expires_in': refresh.lifetime.total_seconds() if refresh.lifetime is not None else 0,
        }
    
    @staticmethod
    def blacklist_token(token: str) -> bool:
        """
        Blacklist a refresh token
        """
        try:
            # Convert the string token to a validated token object
            from rest_framework_simplejwt.tokens import UntypedToken
            validated_token = UntypedToken(token)
            refresh_token = RefreshToken(validated_token)
            refresh_token.blacklist()
            return True
        except Exception as e:
            logger.error(f"Failed to blacklist token: {str(e)}")
            return False


class AuthenticationHelper:
    """
    Helper class for authentication-related utilities
    """
    
    @staticmethod
    def is_authenticated_user(user) -> bool:
        """
        Check if user is authenticated and active
        """
        return (
            user and 
            not isinstance(user, AnonymousUser) and 
            user.is_authenticated and 
    @staticmethod
    def get_user_from_token(token: str) -> Optional["UserType"]:
        """
        Get user from JWT token
        """
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token=token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id, is_active=True)
        except Exception as e:
            logger.error(f"Failed to get user from token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Failed to get user from token: {str(e)}")
            return None
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, list]:
        """
        Validate password strength
        """
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        
        if not any(char.isupper() for char in password):
            errors.append("Password must contain at least one uppercase letter.")
        
        if not any(char.islower() for char in password):
            errors.append("Password must contain at least one lowercase letter.")
        
        if not any(char.isdigit() for char in password):
            errors.append("Password must contain at least one digit.")
        
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
            errors.append("Password must contain at least one special character.")
        
        return len(errors) == 0, errors


class RateLimitedAuthentication(authentication.BaseAuthentication):
    """
    Authentication class with built-in rate limiting
    """
    
    def __init__(self):
        self.auth_attempts = {}  # In production, use Redis or database
        self.max_attempts = 5
        self.lockout_duration = 300  # 5 minutes
    
    def authenticate(self, request):
        """
        Authenticate with rate limiting
        """
        client_ip = self.get_client_ip(request)
        
        if self.is_rate_limited(client_ip):
            raise exceptions.Throttled(
                detail=_('Too many authentication attempts. Please try again later.')
            )
        
        # Proceed with actual authentication (implement your auth logic here)
        # This is a base class - extend it with actual authentication logic
        return None
    
    def get_client_ip(self, request):
        """
        Get client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rate_limited(self, client_ip):
        """
        Check if client IP is rate limited
        """
        import time
        current_time = time.time()
        
        if client_ip in self.auth_attempts:
            attempts, last_attempt = self.auth_attempts[client_ip]
            
            # Reset if lockout duration has passed
            if current_time - last_attempt > self.lockout_duration:
                del self.auth_attempts[client_ip]
                return False
            
            return attempts >= self.max_attempts
        
        return False
    
    def record_failed_attempt(self, client_ip):
        """
        Record a failed authentication attempt
        """
        import time
        current_time = time.time()
        
        if client_ip in self.auth_attempts:
            attempts, _ = self.auth_attempts[client_ip]
            self.auth_attempts[client_ip] = (attempts + 1, current_time)
        else:
            self.auth_attempts[client_ip] = (1, current_time)