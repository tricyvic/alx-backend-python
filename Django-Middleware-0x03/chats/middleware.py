import logging
from datetime import datetime, timedelta
import os
from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponse
from django.utils import timezone
from collections import defaultdict, deque
import time


class RequestLoggingMiddleware:
    """
    Middleware that logs each user's requests to a file, including timestamp, user, and request path.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        
        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response
        
        # Set up logging configuration
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'requests.log')
        
        # Configure logger
        self.logger = logging.getLogger('request_logger')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler if it doesn't exist
        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(file_handler)
    
    def __call__(self, request):
        """
        Process the request and log the information.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            The response from the next middleware or view
        """
        # Get user information
        if request.user.is_authenticated:
            user = request.user.username
        else:
            user = "Anonymous"
        
        # Log the request information
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)
        
        # Process the request through the rest of the middleware chain
        response = self.get_response(request)
        
        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware that restricts access to the messaging app during certain hours.
    Access is denied outside of 6AM to 9PM (18:00 to 21:00).
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        
        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response
        
        # Define allowed hours (6 AM to 9 PM)
        self.start_hour = 6  # 6 AM
        self.end_hour = 21   # 9 PM (21:00)
    
    def __call__(self, request):
        """
        Process the request and check if access is allowed during current time.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            HttpResponseForbidden if access is denied, otherwise the normal response
        """
        # Get current server time
        current_time = timezone.now()
        current_hour = current_time.hour
        
        # Check if the request is for chat/messaging related paths
        # Allow access to admin, static files, and other non-chat paths
        chat_paths = ['/api/v1/', '/admin/', '/conversations', '/messages']
        
        # Check if the current path is related to messaging/chat functionality
        is_chat_request = any(request.path.startswith(path) for path in chat_paths if path != '/admin/')
        
        # If it's a chat-related request and outside allowed hours
        if is_chat_request and not (self.start_hour <= current_hour < self.end_hour):
            # Return 403 Forbidden response
            forbidden_message = f"""
            <html>
            <head><title>Access Restricted</title></head>
            <body>
                <h1>403 Forbidden</h1>
                <p>Access to the messaging app is restricted.</p>
                <p>Please try again between 6:00 AM and 9:00 PM.</p>
                <p>Current server time: {current_time.strftime('%H:%M:%S')}</p>
            </body>
            </html>
            """
            return HttpResponseForbidden(forbidden_message)
        
        # Process the request through the rest of the middleware chain
        response = self.get_response(request)
        
        return response


class OffensiveLanguageMiddleware:
    """
    Middleware that limits the number of chat messages a user can send within a certain time window,
    based on their IP address. Implements rate limiting for POST requests to prevent spam.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        
        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response
        
        # Rate limiting configuration
        self.max_messages_per_minute = 5  # Maximum 5 messages per minute
        self.time_window = 60  # Time window in seconds (1 minute)
        
        # Dictionary to track requests per IP address
        # Structure: {ip_address: deque([timestamp1, timestamp2, ...])}
        self.ip_requests = defaultdict(deque)
        
        # Clean up old entries periodically
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # Clean up every 5 minutes
    
    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        
        Args:
            request: The HTTP request object
            
        Returns:
            str: The client's IP address
        """
        # Check for IP in headers (for load balancers/proxies)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP in the chain
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            # Use the remote address
            ip = request.META.get('REMOTE_ADDR')
        
        return ip
    
    def cleanup_old_requests(self):
        """
        Remove old request timestamps that are outside the time window.
        """
        current_time = time.time()
        cutoff_time = current_time - self.time_window
        
        # Clean up requests older than the time window
        for ip, timestamps in list(self.ip_requests.items()):
            # Remove timestamps older than the cutoff
            while timestamps and timestamps[0] < cutoff_time:
                timestamps.popleft()
            
            # Remove IP entries that have no recent requests
            if not timestamps:
                del self.ip_requests[ip]
    
    def is_rate_limited(self, ip_address):
        """
        Check if the IP address has exceeded the rate limit.
        
        Args:
            ip_address (str): The client's IP address
            
        Returns:
            bool: True if rate limited, False otherwise
        """
        current_time = time.time()
        cutoff_time = current_time - self.time_window
        
        # Get requests for this IP
        timestamps = self.ip_requests[ip_address]
        
        # Remove old timestamps
        while timestamps and timestamps[0] < cutoff_time:
            timestamps.popleft()
        
        # Check if current count exceeds limit
        return len(timestamps) >= self.max_messages_per_minute
    
    def record_request(self, ip_address):
        """
        Record a new request for the IP address.
        
        Args:
            ip_address (str): The client's IP address
        """
        current_time = time.time()
        self.ip_requests[ip_address].append(current_time)
    
    def __call__(self, request):
        """
        Process the request and check for rate limiting on POST requests to messaging endpoints.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            HttpResponse with 429 status if rate limited, otherwise normal response
        """
        # Perform periodic cleanup
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self.cleanup_old_requests()
            self.last_cleanup = current_time
        
        # Check if this is a POST request to messaging endpoints
        messaging_paths = ['/api/v1/messages/', '/api/v1/conversations/', '/messages/', '/conversations/']
        is_messaging_post = (
            request.method == 'POST' and 
            any(request.path.startswith(path) for path in messaging_paths)
        )
        
        if is_messaging_post:
            # Get client IP
            client_ip = self.get_client_ip(request)
            
            # Check if this IP is rate limited
            if self.is_rate_limited(client_ip):
                # Create rate limit response
                rate_limit_message = f"""
                <html>
                <head><title>Rate Limit Exceeded</title></head>
                <body>
                    <h1>429 Too Many Requests</h1>
                    <p>You have exceeded the rate limit for sending messages.</p>
                    <p>Limit: {self.max_messages_per_minute} messages per minute</p>
                    <p>Please wait before sending another message.</p>
                    <p>Your IP: {client_ip}</p>
                    <p>Time: {datetime.now().strftime('%H:%M:%S')}</p>
                </body>
                </html>
                """
                
                # Return 429 Too Many Requests
                response = HttpResponse(rate_limit_message, status=429)
                response['Retry-After'] = str(self.time_window)  # Suggest retry time
                return response
            
            # Record this request
            self.record_request(client_ip)
        
        # Process the request through the rest of the middleware chain
        response = self.get_response(request)
        
        return response



class RolepermissionMiddleware:
    """
    Middleware that checks the user's role before allowing access to specific actions.
    Only admin and moderator users are allowed to perform certain privileged operations.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        
        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response
        
        # Define allowed roles for privileged operations
        self.allowed_roles = ['admin', 'moderator']
        
        # Define paths that require privileged access
        # These paths will require admin or moderator role
        self.protected_paths = [
            '/admin/',                    # Django admin interface
            '/api/v1/admin/',            # Custom admin API endpoints
            '/api/v1/users/',            # User management endpoints
            '/api/v1/conversations/delete/',  # Delete conversations
            '/api/v1/messages/delete/',   # Delete messages
            '/api/v1/moderation/',       # Moderation endpoints
        ]
        
        # Define HTTP methods that require privileged access
        # GET requests are generally allowed, but POST/PUT/DELETE may need restrictions
        self.protected_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    def is_protected_path(self, request_path):
        """
        Check if the request path requires privileged access.
        
        Args:
            request_path (str): The path being requested
            
        Returns:
            bool: True if the path requires privileged access, False otherwise
        """
        # Check if the path starts with any of the protected paths
        return any(request_path.startswith(path) for path in self.protected_paths)
    
    def is_protected_operation(self, request):
        """
        Check if the request is a protected operation that requires role check.
        
        Args:
            request: The HTTP request object
            
        Returns:
            bool: True if the operation requires role check, False otherwise
        """
        # Check if it's a protected path
        if self.is_protected_path(request.path):
            return True
        
        # Check for protected methods on API endpoints
        if (request.method in self.protected_methods and 
            request.path.startswith('/api/v1/')):
            # Allow some endpoints for regular users (like creating conversations/messages)
            allowed_for_all = [
                '/api/v1/conversations/',    # Users can create conversations
                '/api/v1/messages/',         # Users can send messages
            ]
            
            # If it's an exact match to allowed endpoints, don't require role check
            if any(request.path == path or 
                   (request.path.startswith(path) and request.method == 'POST')
                   for path in allowed_for_all):
                return False
            
            return True
        
        return False
    
    def has_required_role(self, user):
        """
        Check if the user has the required role for privileged operations.
        
        Args:
            user: The Django user object
            
        Returns:
            bool: True if user has admin or moderator role, False otherwise
        """
        if not user.is_authenticated:
            return False
        
        # Check if user has one of the allowed roles
        return hasattr(user, 'role') and user.role in self.allowed_roles
    
    def __call__(self, request):
        """
        Process the request and check user role for protected operations.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            HttpResponseForbidden if access denied, otherwise normal response
        """
        # Check if this operation requires role check
        if self.is_protected_operation(request):
            # Check if user has the required role
            if not self.has_required_role(request.user):
                # Determine the reason for denial
                if not request.user.is_authenticated:
                    reason = "Authentication required"
                    user_info = "Not authenticated"
                else:
                    reason = "Insufficient privileges"
                    user_role = getattr(request.user, 'role', 'unknown')
                    user_info = f"User role: {user_role}"
                
                # Create forbidden response
                forbidden_message = f"""
                <html>
                <head><title>Access Denied</title></head>
                <body>
                    <h1>403 Forbidden</h1>
                    <p><strong>Access Denied:</strong> {reason}</p>
                    <p>This operation requires admin or moderator privileges.</p>
                    <p><strong>Required roles:</strong> {', '.join(self.allowed_roles)}</p>
                    <p><strong>Your status:</strong> {user_info}</p>
                    <p><strong>Requested path:</strong> {request.path}</p>
                    <p><strong>Method:</strong> {request.method}</p>
                    <p><strong>Time:</strong> {datetime.now().strftime('%H:%M:%S')}</p>
                </body>
                </html>
                """
                
                return HttpResponseForbidden(forbidden_message)
        
        # Process the request through the rest of the middleware chain
        response = self.get_response(request)
        
        return response
