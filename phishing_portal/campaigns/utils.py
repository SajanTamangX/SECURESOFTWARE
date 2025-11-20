from .models import AuditLog
import hashlib


def get_client_ip(request):
    ip = request.META.get("REMOTE_ADDR", "")
    return hashlib.sha256(ip.encode()).hexdigest() if ip else ""


def log_action(request, action, details=""):
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        details=details,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
    )

