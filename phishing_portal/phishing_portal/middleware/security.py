"""
Security middleware for blocking common web attacks.

This module provides middleware to protect against:
- XSS (Cross-Site Scripting) attacks
- JavaScript injection attempts
- Event handler injection (onerror, onload, etc.)

Note: This is a basic first line of defense. Django's built-in protections
(CSRF tokens, template escaping) provide additional security layers.
"""

from django.http import HttpResponseForbidden


class BlockCommonAttacksMiddleware:
    """
    Middleware to block obvious XSS attempts in query strings.
    
    This middleware scans GET parameters for suspicious patterns that indicate
    XSS attack attempts. If detected, it returns a 403 Forbidden response.
    
    Security features:
    - Blocks <script> tags in URLs
    - Blocks javascript: protocol handlers
    - Blocks event handler attributes (onerror, onload, etc.)
    
    Note: This is not comprehensive but catches obvious attack patterns.
    Django's template escaping and CSRF protection provide additional layers.
    
    Usage:
        Add to MIDDLEWARE in settings.py:
        'phishing_portal.middleware.security.BlockCommonAttacksMiddleware'
    """
    def __init__(self, get_response):
        """
        Initialize middleware.
        
        Args:
            get_response: Django's get_response callable
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process request and check for suspicious patterns.
        
        Scans GET query parameters for common XSS attack patterns.
        Returns 403 Forbidden if suspicious patterns are detected.
        
        Args:
            request: Django HttpRequest object
        
        Returns:
            HttpResponse: Either 403 Forbidden or passes to next middleware
        """
        # List of suspicious patterns that indicate XSS attempts
        # Could expand this list based on attack patterns observed
        suspicious = [
            "<script",      # Script tag injection
            "javascript:",  # JavaScript protocol handler
            "onerror",      # Event handler injection
            "onload"        # Event handler injection
        ]
        
        # Get URL-encoded query string and convert to lowercase for case-insensitive matching
        query = request.GET.urlencode().lower()
        
        # Check if any suspicious pattern is found in query string
        if any(x in query for x in suspicious):
            # Return 403 Forbidden response
            return HttpResponseForbidden("Potential XSS detected")
        
        # No suspicious patterns found, continue to next middleware/view
        return self.get_response(request)

