from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if request.user.role not in allowed_roles:
                # Log permission denied event
                from campaigns.utils import log_action
                log_action(
                    request,
                    "Permission denied - role check failed",
                    f"User: {request.user.username}, Role: {request.user.role}, "
                    f"Required roles: {', '.join(allowed_roles)}, "
                    f"View: {view_func.__name__}, Path: {request.path}"
                )
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator

