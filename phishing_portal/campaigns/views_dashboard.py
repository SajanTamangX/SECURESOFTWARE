import json
from datetime import datetime, timedelta
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from accounts.decorators import role_required
from .models import Campaign, Recipient, Event, CampaignRecipient


@role_required("ADMIN", "INSTRUCTOR")
def dashboard(request):
    # Basic counts
    total_campaigns = Campaign.objects.count()
    total_recipients = Recipient.objects.count()
    total_events = Event.objects.count()
    
    # Past 7 days events
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_events = Event.objects.filter(created_at__gte=seven_days_ago)
    
    opens = recent_events.filter(event_type=Event.Type.OPEN).count()
    clicks = recent_events.filter(event_type=Event.Type.CLICK).count()
    reports = recent_events.filter(event_type=Event.Type.REPORT).count()
    
    # Daily breakdown for chart (last 7 days)
    daily_data = []
    for i in range(6, -1, -1):
        day = timezone.now() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        day_opens = Event.objects.filter(
            event_type=Event.Type.OPEN,
            created_at__range=(day_start, day_end)
        ).count()
        day_clicks = Event.objects.filter(
            event_type=Event.Type.CLICK,
            created_at__range=(day_start, day_end)
        ).count()
        day_reports = Event.objects.filter(
            event_type=Event.Type.REPORT,
            created_at__range=(day_start, day_end)
        ).count()
        
        daily_data.append({
            "date": day.strftime("%m/%d"),
            "opens": day_opens,
            "clicks": day_clicks,
            "reports": day_reports,
        })
    
    # Top 5 campaigns by clicks
    top_campaigns = (
        Campaign.objects
        .annotate(
            click_count=Count(
                "campaign_recipients__events",
                filter=Q(campaign_recipients__events__event_type=Event.Type.CLICK),
                distinct=True
            )
        )
        .filter(click_count__gt=0)
        .order_by("-click_count")[:5]
    )
    
    # Engagement rate calculation
    total_recipients_with_events = (
        CampaignRecipient.objects
        .filter(events__isnull=False)
        .distinct()
        .count()
    )
    total_campaign_recipients = CampaignRecipient.objects.count()
    engagement_rate = (
        (total_recipients_with_events / total_campaign_recipients * 100)
        if total_campaign_recipients > 0
        else 0
    )
    
    return render(
        request,
        "dashboard.html",
        {
            "total_campaigns": total_campaigns,
            "total_recipients": total_recipients,
            "total_events": total_events,
            "opens": opens,
            "clicks": clicks,
            "reports": reports,
            "daily_data": json.dumps(daily_data),
            "top_campaigns": top_campaigns,
            "engagement_rate": round(engagement_rate, 1),
        },
    )

