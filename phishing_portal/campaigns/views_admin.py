from django.shortcuts import render
from django.core.paginator import Paginator
from accounts.decorators import role_required
from .models import AuditLog


@role_required("ADMIN")
def audit_logs(request):
    logs = AuditLog.objects.select_related("user").all()
    
    # Filtering by user
    user_filter = request.GET.get("user", "")
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    
    # Filtering by action
    action_filter = request.GET.get("action", "")
    if action_filter:
        logs = logs.filter(action__icontains=action_filter)
    
    # Pagination
    paginator = Paginator(logs, 25)
    page = request.GET.get("page")
    logs_page = paginator.get_page(page)
    
    # Get unique users and actions for filter dropdowns
    unique_users = AuditLog.objects.values_list("user__username", flat=True).distinct().exclude(user__isnull=True).order_by("user__username")
    unique_actions = AuditLog.objects.values_list("action", flat=True).distinct().order_by("action")
    
    return render(request, "admin/audit_logs.html", {
        "logs": logs_page,
        "user_filter": user_filter,
        "action_filter": action_filter,
        "unique_users": unique_users,
        "unique_actions": unique_actions,
    })

