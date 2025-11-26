import csv
import io
import hashlib

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from .forms import EmailTemplateForm, CampaignForm, RecipientUploadForm
from .models import EmailTemplate, Campaign, Recipient, CampaignRecipient, Event, CampaignEmail
from .utils import log_action
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden


# --- Email Templates ---

@login_required
def template_list(request):
    templates = EmailTemplate.objects.all()
    
    # Search
    q = request.GET.get("q", "")
    if q:
        templates = templates.filter(name__icontains=q)
    
    # Pagination
    paginator = Paginator(templates, 10)
    page = request.GET.get("page")
    templates_page = paginator.get_page(page)
    
    return render(request, "campaigns/template_list.html", {
        "templates": templates_page,
        "query": q,
    })


@role_required("ADMIN", "INSTRUCTOR")
def template_create(request):
    if request.method == "POST":
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            tmpl = form.save(commit=False)
            tmpl.created_by = request.user
            tmpl.save()
            log_action(request, "Created email template", f"Template: {tmpl.name} (ID: {tmpl.id})")
            messages.success(request, "Email template created.")
            return redirect("campaigns:template_list")
    else:
        form = EmailTemplateForm()
    return render(request, "campaigns/template_form.html", {"form": form})


# --- Campaigns ---

@login_required
def campaign_list(request):
    campaigns = Campaign.objects.select_related("email_template", "created_by")
    
    # Search
    q = request.GET.get("q", "")
    if q:
        campaigns = campaigns.filter(name__icontains=q)
    
    # Pagination
    paginator = Paginator(campaigns, 10)
    page = request.GET.get("page")
    campaigns_page = paginator.get_page(page)
    
    return render(request, "campaigns/campaign_list.html", {
        "campaigns": campaigns_page,
        "query": q,
    })


@role_required("ADMIN", "INSTRUCTOR")
def campaign_create(request):
    if request.method == "POST":
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.created_by = request.user
            campaign.save()
            log_action(request, "Created campaign", f"Campaign: {campaign.name} (ID: {campaign.id})")
            messages.success(request, "Campaign created.")
            return redirect("campaigns:campaign_detail", pk=campaign.pk)
    else:
        form = CampaignForm()
    return render(request, "campaigns/campaign_form.html", {"form": form})


@login_required
def campaign_detail(request, pk):
    campaign = get_object_or_404(
        Campaign.objects.select_related("email_template", "created_by"),
        pk=pk,
    )
    recipients = (
        CampaignRecipient.objects
        .select_related("recipient")
        .filter(campaign=campaign)
    )
    
    # Metrics
    events = Event.objects.filter(campaign_recipient__campaign=campaign)
    total_recipients = recipients.count()
    opens = events.filter(event_type=Event.Type.OPEN).values("campaign_recipient").distinct().count()
    clicks = events.filter(event_type=Event.Type.CLICK).values("campaign_recipient").distinct().count()
    reports = events.filter(event_type=Event.Type.REPORT).values("campaign_recipient").distinct().count()
    
    metrics = {
        "total_recipients": total_recipients,
        "unique_opens": opens,
        "unique_clicks": clicks,
        "unique_reports": reports,
    }
    
    return render(
        request,
        "campaigns/campaign_detail.html",
        {
            "campaign": campaign,
            "recipients": recipients,
            "metrics": metrics,
        },
    )


@role_required("ADMIN", "INSTRUCTOR")
def upload_recipients(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if request.method == "POST":
        form = RecipientUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data["csv_file"]
            decoded = csv_file.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(decoded))

            created_count = 0
            linked_count = 0

            with transaction.atomic():
                for row in reader:
                    email = row.get("email", "").strip()
                    if not email:
                        continue

                    first_name = row.get("first_name", "").strip()
                    last_name = row.get("last_name", "").strip()
                    department = row.get("department", "").strip()

                    recipient, created = Recipient.objects.get_or_create(
                        email=email,
                        defaults={
                            "first_name": first_name,
                            "last_name": last_name,
                            "department": department,
                        },
                    )

                    if created:
                        created_count += 1

                    _, link_created = CampaignRecipient.objects.get_or_create(
                        campaign=campaign,
                        recipient=recipient,
                    )

                    if link_created:
                        linked_count += 1

            log_action(
                request,
                "Uploaded recipients",
                f"Campaign: {campaign.name} (ID: {campaign.id}) - {created_count} new, {linked_count} linked"
            )
            messages.success(
                request,
                f"Upload complete. {created_count} new recipients, "
                f"{linked_count} linked to this campaign.",
            )
            return redirect("campaigns:campaign_detail", pk=campaign.pk)
    else:
        form = RecipientUploadForm()
    return render(
        request,
        "campaigns/recipient_upload.html",
        {"campaign": campaign, "form": form},
    )


# --- Tracking & Landing Page ---

def _hash_ip(ip: str) -> str:
    if not ip:
        return ""
    # Simple one-way hash to avoid storing raw IPs
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()


def _log_event(tracking_id, event_type, request):
    try:
        cr = CampaignRecipient.objects.select_related("campaign").get(
            tracking_id=tracking_id, is_active=True
        )
    except CampaignRecipient.DoesNotExist:
        raise Http404("Unknown tracking id")
    
    user_agent = request.META.get("HTTP_USER_AGENT", "")[:255]
    ip = request.META.get("REMOTE_ADDR", "")
    
    Event.objects.create(
        campaign_recipient=cr,
        event_type=event_type,
        user_agent=user_agent,
        ip_hash=_hash_ip(ip),
    )
    return cr


# 1x1 transparent PNG (so that email clients load it)
PIXEL_DATA = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\xdacd\xf8\x0f\x00\x01\x01\x01\x00"
    b"\x18\xdd\x8d\xb1\x00\x00\x00\x00IEND\xaeB`\x82"
)


@csrf_exempt  # tracking pixel is GET-only and has no form data
def track_open(request, tracking_id):
    _log_event(tracking_id, Event.Type.OPEN, request)
    # Return a tiny PNG pixel
    return HttpResponse(PIXEL_DATA, content_type="image/png")


@csrf_exempt
def track_click(request, tracking_id):
    cr = _log_event(tracking_id, Event.Type.CLICK, request)
    # Redirect to learning landing page
    url = reverse("campaigns:landing_page", kwargs={"tracking_id": tracking_id})
    return HttpResponseRedirect(url)


@csrf_exempt
def track_report(request, tracking_id):
    cr = _log_event(tracking_id, Event.Type.REPORT, request)
    url = reverse("campaigns:landing_page", kwargs={"tracking_id": tracking_id})
    return HttpResponseRedirect(url)


def landing_page(request, tracking_id):
    try:
        cr = CampaignRecipient.objects.select_related(
            "campaign", "recipient", "campaign__email_template"
        ).get(tracking_id=tracking_id)
    except CampaignRecipient.DoesNotExist:
        raise Http404("Unknown tracking id")
    
    template = cr.campaign.email_template
    learning_points = template.learning_points or "This was a simulated phishing email designed to test awareness."
    
    # Count events for this recipient
    events = cr.events.order_by("created_at")
    opened = events.filter(event_type=Event.Type.OPEN).exists()
    clicked = events.filter(event_type=Event.Type.CLICK).exists()
    reported = events.filter(event_type=Event.Type.REPORT).exists()
    
    return render(
        request,
        "campaigns/landing_page.html",
        {
            "campaign_recipient": cr,
            "template": template,
            "learning_points": learning_points,
            "events": events,
            "opened": opened,
            "clicked": clicked,
            "reported": reported,
        },
    )


# --- Email Sending ---

@role_required("ADMIN", "INSTRUCTOR")
def send_campaign(request, pk):
    from .services import send_campaign_emails
    
    campaign = get_object_or_404(Campaign, pk=pk)
    if request.method == "POST":
        send_campaign_emails(campaign, request=request)
        recipient_count = campaign.campaign_recipients.count()
        log_action(
            request,
            "Sent campaign emails",
            f"Campaign: {campaign.name} (ID: {campaign.id}) - {recipient_count} recipients"
        )
        messages.success(request, "Emails sent for this campaign (check MailHog).")
        return redirect("campaigns:campaign_detail", pk=campaign.pk)
    return redirect("campaigns:campaign_detail", pk=campaign.pk)


# --- Inbox ---

@login_required
def inbox(request):
    """
    Simple inbox showing emails for the logged-in user.
    For VIEWER role, filter by their email address.
    For ADMIN/INSTRUCTOR you may show all emails (or also filter – up to you).
    """
    qs = CampaignEmail.objects.all().select_related("campaign", "recipient", "recipient__recipient")

    user = request.user
    # If the user has an email address, filter emails by that
    if user.email:
        qs = qs.filter(recipient__recipient__email=user.email)

    context = {
        "emails": qs,
        "user_role": user.role,
    }
    return render(request, "campaigns/inbox.html", context)


@login_required
def inbox_detail(request, pk: int):
    email_obj = get_object_or_404(
        CampaignEmail.objects.select_related("campaign", "recipient", "recipient__recipient"),
        pk=pk,
    )

    user = request.user
    # Safety check: VIEWERs can only see messages sent to their own email
    if user.email and email_obj.recipient.recipient.email != user.email and user.role == "VIEWER":
        return HttpResponseForbidden("You are not allowed to view this email.")

    if not email_obj.is_read:
        email_obj.is_read = True
        email_obj.save(update_fields=["is_read"])

    return render(request, "campaigns/inbox_detail.html", {"email": email_obj})


@login_required
@require_POST
def toggle_email_read(request, pk: int):
    email_obj = get_object_or_404(CampaignEmail, pk=pk)

    user = request.user
    # VIEWERs can only toggle their own emails
    if user.role == "VIEWER" and user.email:
        if email_obj.recipient.recipient.email != user.email:
            return HttpResponseForbidden("You are not allowed to modify this email.")

    email_obj.is_read = not email_obj.is_read
    email_obj.save(update_fields=["is_read"])
    return redirect("campaigns:inbox")


# --- Blog Features (Available to All Roles) ---

from .blog_posts import BLOG_POSTS

@login_required
def blog_list(request, role):
    """Blog list page for all roles (viewer, instructor, admin)"""
    # Validate role
    if role not in ['viewer', 'instructor', 'admin']:
        raise Http404("Invalid role")
    
    posts = sorted(BLOG_POSTS, key=lambda p: p["published"], reverse=True)
    return render(request, f"{role}/blog_list.html", {"posts": posts, "role": role})


@login_required
def blog_detail(request, role, slug):
    """Blog detail page for all roles"""
    # Validate role
    if role not in ['viewer', 'instructor', 'admin']:
        raise Http404("Invalid role")
    
    post = next((p for p in BLOG_POSTS if p["slug"] == slug), None)
    if not post:
        raise Http404("Post not found")
    
    return render(request, f"{role}/blog_detail.html", {
        "post": post,
        "all_posts": BLOG_POSTS,
        "role": role,
    })


# --- Viewer Features: Sticky Notes ---


@login_required
def viewer_notes_board(request):
    from .models import StickyNote
    
    notes = StickyNote.objects.filter(user=request.user).order_by("is_done", "-created_at")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        body = request.POST.get("body", "").strip()
        priority = request.POST.get("priority", "medium")
        if title:
            StickyNote.objects.create(
                user=request.user,
                title=title,
                body=body,
                priority=priority,
            )
        return redirect("campaigns:viewer_notes_board")

    return render(request, "viewer/notes_board.html", {"notes": notes})


@login_required
@require_POST
def viewer_note_toggle(request, note_id):
    from .models import StickyNote
    
    note = StickyNote.objects.filter(id=note_id, user=request.user).first()
    if note:
        note.is_done = not note.is_done
        note.save()
    return redirect("campaigns:viewer_notes_board")


@login_required
def training_videos(request):
    """Display professional phishing awareness training videos."""
    return render(request, "campaigns/training_videos.html")
