from .models import AuditLog
import hashlib


def get_client_ip(request):
    ip = request.META.get("REMOTE_ADDR", "")
    return hashlib.sha256(ip.encode()).hexdigest() if ip else ""


def log_action(request, action, details=""):
    """
    Log an action to the audit log.
    
    Args:
        request: Django HttpRequest object (can be None for service-layer calls)
        action: Action description string
        details: Additional details string
    """
    AuditLog.objects.create(
        user=request.user if request and request.user.is_authenticated else None,
        action=action,
        details=details,
        ip_address=get_client_ip(request) if request else "",
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:255] if request else "",
    )

