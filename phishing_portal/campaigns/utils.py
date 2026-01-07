"""
Utility functions for the Campaigns app.

This module provides helper functions for:
- IP address hashing (privacy compliance)
- Audit logging (security event tracking)
"""

from .models import AuditLog
import hashlib


def get_client_ip(request):
    """
    Get and hash the client IP address from request.
    
    Security: IP addresses are hashed using SHA-256 for privacy compliance.
    We don't store raw IP addresses to protect user privacy.
    
    Args:
        request: Django HttpRequest object
    
    Returns:
        str: SHA-256 hash of IP address, or empty string if no IP found
    """
    ip = request.META.get("REMOTE_ADDR", "")
    # Hash IP address using SHA-256 (one-way hash, cannot be reversed)
    return hashlib.sha256(ip.encode()).hexdigest() if ip else ""


def log_action(request, action, details=""):
    """
    Log an action to the audit log for security tracking.
    
    Creates an audit log entry with:
    - User who performed the action (if authenticated)
    - Action description
    - Additional details
    - Hashed IP address (for privacy)
    - User agent string
    
    Args:
        request: Django HttpRequest object (can be None for service-layer calls)
        action: Action description string (e.g., "Created campaign", "Failed login")
        details: Additional details string (e.g., "Campaign: Test Campaign (ID: 123)")
    
    Example:
        log_action(request, "Created campaign", "Campaign: Test Campaign (ID: 123)")
        log_action(None, "CSV import completed", "Created 50 recipients")
    """
    AuditLog.objects.create(
        user=request.user if request and request.user.is_authenticated else None,
        action=action,
        details=details,
        ip_address=get_client_ip(request) if request else "",  # Hashed IP for privacy
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:255] if request else "",  # Truncate to max length
    )

