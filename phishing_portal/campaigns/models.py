"""
Django models for the Phishing Portal Campaigns application.

This module defines the database models for:
- Email templates (pre-built scenarios and custom HTML)
- Campaigns (phishing simulation campaigns)
- Recipients (email recipients for campaigns)
- Events (tracking opens, clicks, reports)
- Audit logs (security event logging)
- Campaign emails (sent email records)
- Sticky notes (user notes feature)
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class EmailTemplate(models.Model):
    """
    Email template model for creating phishing email templates.
    
    Supports two types of templates:
    1. SCENARIO: Pre-built phishing scenarios (IT alerts, password reset, etc.)
    2. CUSTOM: Custom HTML email templates
    
    Templates can include placeholders like {{ first_name }}, {{ click_url }}, etc.
    """
    # Pre-defined phishing scenario types
    # These scenarios have built-in HTML templates for realistic phishing emails
    class Scenario(models.TextChoices):
        IT_ALERT = "IT_ALERT", "IT Security Alert"              # Security alert phishing scenario
        PASSWORD_RESET = "PASSWORD_RESET", "Password Reset"    # Password reset phishing scenario
        PAYROLL = "PAYROLL", "Payroll / Bank Details"          # Payroll/banking phishing scenario
        DELIVERY = "DELIVERY", "Delivery Failure"               # Delivery notification phishing scenario
        HR_POLICY = "HR_POLICY", "HR Policy Update"            # HR policy update phishing scenario
        GENERAL = "GENERAL", "General internal email"          # Normal internal email (not phishing)

    # Template type choices
    # Determines how the email body is rendered
    class TemplateType(models.TextChoices):
        SCENARIO = "SCENARIO", "Pre-built Scenario"  # Use pre-built scenario HTML templates
        CUSTOM = "CUSTOM", "Custom HTML Email"       # Use custom HTML from html_content field

    name = models.CharField(max_length=150, unique=True)
    subject = models.CharField(max_length=200)
    body = models.TextField(
        help_text="Optional extra text. Placeholders like {{ first_name }} are allowed.",
        blank=True,
    )
    template_type = models.CharField(
        max_length=20,
        choices=TemplateType.choices,
        default=TemplateType.SCENARIO,
        help_text="Choose between pre-built scenario or custom HTML email.",
    )
    scenario = models.CharField(
        max_length=30,
        choices=Scenario.choices,
        blank=True,
        default=Scenario.IT_ALERT,
        help_text="Which built-in phishing scenario layout to use (only for scenario type). Use 'General internal email' for normal HR / IT / company announcements that are not meant to look like phishing.",
    )
    html_content = models.TextField(
        blank=True,
        help_text="Custom HTML email content. Use placeholders like {{ first_name }}, {{ click_url }}, {{ report_url }}. Only used when template_type is CUSTOM.",
    )
    sender_email = models.EmailField(
        blank=True,
        max_length=254,
        help_text="Sender email address (e.g., 'security@company.com'). If empty, uses system default.",
    )
    sender_name = models.CharField(
        blank=True,
        max_length=200,
        help_text="Sender display name (e.g., 'IT Security Team')",
    )
    learning_points = models.TextField(
        blank=True,
        help_text="Short explanation shown on the landing page (why this email was suspicious)."
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_templates",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Recipient(models.Model):
    """
    Recipient model for storing email recipient information.
    
    Recipients can be linked to multiple campaigns through CampaignRecipient.
    Email addresses are stored in lowercase for consistency.
    """
    # Email address (primary identifier)
    email = models.EmailField()
    # Optional recipient information
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)

    class Meta:
        # Index on email for faster lookups
        indexes = [
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.email


class Campaign(models.Model):
    """
    Campaign model for managing phishing simulation campaigns.
    
    A campaign links an email template with recipients and tracks the campaign status.
    Campaigns can be scheduled for future execution or sent immediately.
    """
    # Campaign status choices - tracks the lifecycle of a campaign
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"              # Campaign is being created/edited
        SCHEDULED = "SCHEDULED", "Scheduled"   # Campaign is scheduled for future sending
        ACTIVE = "ACTIVE", "Active"            # Campaign is currently active
        PAUSED = "PAUSED", "Paused"            # Campaign is temporarily paused
        COMPLETED = "COMPLETED", "Completed"    # Campaign has finished
        CANCELLED = "CANCELLED", "Cancelled"   # Campaign was cancelled

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    email_template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.PROTECT,
        related_name="campaigns",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="campaigns",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_for = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Planned start date/time for this campaign."
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When emails were actually sent."
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class CampaignRecipient(models.Model):
    """
    Many-to-many relationship between Campaign and Recipient.
    
    This model links recipients to campaigns and provides:
    - Unique tracking ID for each recipient-campaign pair (for email tracking)
    - Ability to activate/deactivate recipients per campaign
    - Timestamp tracking for when recipients were added
    """
    # Foreign key to Campaign
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,  # Delete links if campaign is deleted
        related_name="campaign_recipients",
    )
    # Foreign key to Recipient
    recipient = models.ForeignKey(
        Recipient,
        on_delete=models.CASCADE,  # Delete links if recipient is deleted
        related_name="campaign_memberships",
    )
    # Unique UUID for tracking email opens/clicks/reports
    # This is embedded in email links to track recipient interactions
    tracking_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    # Flag to enable/disable recipient for this campaign
    is_active = models.BooleanField(default=True)
    # Timestamp when recipient was added to campaign
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure a recipient can only be linked to a campaign once
        unique_together = ("campaign", "recipient")

    def __str__(self):
        return f"{self.campaign.name} – {self.recipient.email}"


class Event(models.Model):
    """
    Event model for tracking recipient interactions with phishing emails.
    
    Tracks three types of events:
    - OPEN: Email was opened (via tracking pixel)
    - CLICK: Link in email was clicked
    - REPORT: Recipient reported the email as phishing
    
    Stores hashed IP addresses for privacy compliance.
    """
    # Event type choices
    class Type(models.TextChoices):
        OPEN = "OPEN", "Open"      # Email opened (tracked via 1x1 pixel)
        CLICK = "CLICK", "Click"   # Link clicked in email
        REPORT = "REPORT", "Report" # Email reported as phishing

    # Link to the campaign-recipient pair that triggered this event
    campaign_recipient = models.ForeignKey(
        CampaignRecipient,
        on_delete=models.CASCADE,  # Delete events if campaign-recipient link is deleted
        related_name="events",
    )
    # Type of event (OPEN, CLICK, or REPORT)
    event_type = models.CharField(max_length=10, choices=Type.choices)
    # Timestamp when event occurred
    created_at = models.DateTimeField(default=timezone.now)
    # User agent string from browser (for analytics)
    user_agent = models.CharField(max_length=255, blank=True)
    # SHA-256 hash of IP address (for privacy - we don't store raw IPs)
    ip_hash = models.CharField(max_length=64, blank=True)

    class Meta:
        # Indexes for faster queries on event type and date
        indexes = [
            models.Index(fields=["event_type"]),  # Filter by event type
            models.Index(fields=["created_at"]),  # Filter by date
        ]

    def __str__(self):
        return f"{self.event_type} – {self.campaign_recipient}"


class AuditLog(models.Model):
    """
    Audit log model for security event logging.
    
    Records all significant actions in the system for security auditing:
    - User actions (login, logout, create campaign, etc.)
    - Permission denials
    - Suspicious activities
    - System changes
    
    Stores hashed IP addresses for privacy compliance.
    """
    # User who performed the action (null if action was system-generated)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # Keep log even if user is deleted
        null=True
    )
    # Description of the action performed
    action = models.CharField(max_length=255)
    # Additional details about the action
    details = models.TextField(blank=True)
    # SHA-256 hash of IP address (for privacy - we don't store raw IPs)
    ip_address = models.CharField(max_length=64, blank=True)
    # User agent string from browser
    user_agent = models.CharField(max_length=255, blank=True)
    # Timestamp when action occurred
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        # Order by most recent first
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at} - {self.user} - {self.action}"


class CampaignEmail(models.Model):
    """
    CampaignEmail model for storing sent email records.
    
    This model stores a copy of every email sent as part of a campaign.
    Used for the inbox feature where users can view emails sent to them.
    """
    # Campaign this email belongs to
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,  # Delete emails if campaign is deleted
        related_name="sent_emails",
    )
    # Campaign-recipient link (contains tracking_id)
    recipient = models.ForeignKey(
        CampaignRecipient,
        on_delete=models.CASCADE,  # Delete emails if recipient link is deleted
        related_name="emails",
    )
    # Email subject line
    subject = models.CharField(max_length=255)
    # Plain text version of email body
    body_text = models.TextField()
    # HTML version of email body
    body_html = models.TextField(blank=True)
    # Timestamp when email was sent
    sent_at = models.DateTimeField(default=timezone.now)
    # Whether recipient has marked email as read (for inbox feature)
    is_read = models.BooleanField(default=False)

    class Meta:
        # Order by most recent first
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.recipient.recipient.email} – {self.subject} – {self.sent_at}"


class StickyNote(models.Model):
    """
    StickyNote model for user notes/reminders feature.
    
    Allows users (primarily VIEWER role) to create personal notes/reminders.
    Notes can have priorities and completion status.
    """
    # Priority level choices for notes
    PRIORITY_CHOICES = [
        ("low", "Low"),       # Low priority note
        ("medium", "Medium"), # Medium priority note (default)
        ("high", "High"),     # High priority note
    ]

    # User who owns this note
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # Delete notes if user is deleted
        related_name="sticky_notes",
    )
    # Note title
    title = models.CharField(max_length=120)
    # Note body/content
    body = models.TextField(blank=True)
    # Priority level (low, medium, high)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    # Whether note is completed/done
    is_done = models.BooleanField(default=False)
    # Timestamp when note was created
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Order: incomplete first, then by priority (high to low), then newest first
        ordering = ["is_done", "-priority", "-created_at"]

    def __str__(self):
        return self.title
