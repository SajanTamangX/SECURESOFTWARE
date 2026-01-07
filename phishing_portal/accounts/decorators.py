"""
Decorators for access control and authorization.

This module provides decorators for:
- Role-based access control (RBAC)
- Permission checking
"""

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login


def role_required(*allowed_roles):
    """
    Decorator to restrict view access based on user roles.
    
    Usage:
        @role_required("ADMIN", "INSTRUCTOR")
        def my_view(request):
            # Only ADMIN and INSTRUCTOR users can access this view
            pass
    
    Args:
        *allowed_roles: Variable number of role strings (e.g., "ADMIN", "INSTRUCTOR")
    
    Behavior:
        - If user is not authenticated: redirects to login page
        - If user's role is not in allowed_roles: raises PermissionDenied and logs the attempt
        - If user's role is in allowed_roles: allows access to the view
    
    Security:
        - Logs all permission denied attempts for security auditing
        - Preserves function metadata using @wraps decorator
    """
    def decorator(view_func):
        @wraps(view_func)  # Preserve function metadata (name, docstring, etc.)
        def _wrapped(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                # Redirect to login page, preserving the original URL
                return redirect_to_login(request.get_full_path())
            
            # Check if user's role is in allowed roles
            if request.user.role not in allowed_roles:
                # Log permission denied event for security auditing
                from campaigns.utils import log_action
                log_action(
                    request,
                    "Permission denied - role check failed",
                    f"User: {request.user.username}, Role: {request.user.role}, "
                    f"Required roles: {', '.join(allowed_roles)}, "
                    f"View: {view_func.__name__}, Path: {request.path}"
                )
                # Raise PermissionDenied exception (returns 403 Forbidden)
                raise PermissionDenied
            
            # User has required role, allow access
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator

