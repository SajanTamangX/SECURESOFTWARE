import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from accounts.decorators import role_required
from .models import Campaign, CampaignRecipient, Event, AuditLog


@role_required("ADMIN", "INSTRUCTOR")
def export_campaign_recipients(request, pk):
    """Export campaign recipients as CSV."""
    campaign = get_object_or_404(Campaign, pk=pk)
    
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="campaign_{campaign.id}_recipients.csv"'
    
    writer = csv.writer(response)
    writer.writerow(["Email", "First Name", "Last Name", "Department", "Tracking ID", "Is Active"])
    
    recipients = CampaignRecipient.objects.filter(
        campaign=campaign
    ).select_related("recipient")
    
    for cr in recipients:
        writer.writerow([
            cr.recipient.email,
            cr.recipient.first_name,
            cr.recipient.last_name,
            cr.recipient.department,
            str(cr.tracking_id),
            "Yes" if cr.is_active else "No",
        ])
    
    return response


@role_required("ADMIN", "INSTRUCTOR")
def export_campaign_events(request, pk):
    """Export campaign events as CSV."""
    campaign = get_object_or_404(Campaign, pk=pk)
    
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="campaign_{campaign.id}_events.csv"'
    
    writer = csv.writer(response)
    writer.writerow(["Event Type", "Recipient Email", "Timestamp", "IP Hash", "User Agent"])
    
    events = Event.objects.filter(
        campaign_recipient__campaign=campaign
    ).select_related("campaign_recipient__recipient").order_by("-created_at")
    
    for event in events:
        writer.writerow([
            event.get_event_type_display(),
            event.campaign_recipient.recipient.email,
            event.created_at.isoformat(),
            event.ip_hash,
            event.user_agent,
        ])
    
    return response


@role_required("ADMIN")
def export_audit_logs(request):
    """Export audit logs as CSV."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="audit_logs.csv"'
    
    writer = csv.writer(response)
    writer.writerow(["Timestamp", "User", "Action", "Details", "IP Address", "User Agent"])
    
    logs = AuditLog.objects.select_related("user").order_by("-created_at")
    
    for log in logs:
        writer.writerow([
            log.created_at.isoformat(),
            log.user.username if log.user else "System",
            log.action,
            log.details,
            log.ip_address,
            log.user_agent,
        ])
    
    return response

