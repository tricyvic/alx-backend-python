import logging
from datetime import datetime
import os
from django.conf import settings


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
