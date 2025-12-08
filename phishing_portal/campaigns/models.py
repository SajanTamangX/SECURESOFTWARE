import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class EmailTemplate(models.Model):
    class Scenario(models.TextChoices):
        IT_ALERT = "IT_ALERT", "IT Security Alert"
        PASSWORD_RESET = "PASSWORD_RESET", "Password Reset"
        PAYROLL = "PAYROLL", "Payroll / Bank Details"
        DELIVERY = "DELIVERY", "Delivery Failure"
        HR_POLICY = "HR_POLICY", "HR Policy Update"
        GENERAL = "GENERAL", "General internal email"

    class TemplateType(models.TextChoices):
        SCENARIO = "SCENARIO", "Pre-built Scenario"
        CUSTOM = "CUSTOM", "Custom HTML Email"

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
    email = models.EmailField()
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.email


class Campaign(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SCHEDULED = "SCHEDULED", "Scheduled"
        ACTIVE = "ACTIVE", "Active"
        PAUSED = "PAUSED", "Paused"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

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
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="campaign_recipients",
    )
    recipient = models.ForeignKey(
        Recipient,
        on_delete=models.CASCADE,
        related_name="campaign_memberships",
    )
    tracking_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("campaign", "recipient")

    def __str__(self):
        return f"{self.campaign.name} – {self.recipient.email}"


class Event(models.Model):
    class Type(models.TextChoices):
        OPEN = "OPEN", "Open"
        CLICK = "CLICK", "Click"
        REPORT = "REPORT", "Report"

    campaign_recipient = models.ForeignKey(
        CampaignRecipient,
        on_delete=models.CASCADE,
        related_name="events",
    )
    event_type = models.CharField(max_length=10, choices=Type.choices)
    created_at = models.DateTimeField(default=timezone.now)
    user_agent = models.CharField(max_length=255, blank=True)
    ip_hash = models.CharField(max_length=64, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["event_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} – {self.campaign_recipient}"


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    ip_address = models.CharField(max_length=64, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at} - {self.user} - {self.action}"


class CampaignEmail(models.Model):
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="sent_emails",
    )
    recipient = models.ForeignKey(
        CampaignRecipient,
        on_delete=models.CASCADE,
        related_name="emails",
    )
    subject = models.CharField(max_length=255)
    body_text = models.TextField()
    body_html = models.TextField(blank=True)
    sent_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.recipient.recipient.email} – {self.subject} – {self.sent_at}"


class StickyNote(models.Model):
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sticky_notes",
    )
    title = models.CharField(max_length=120)
    body = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["is_done", "-priority", "-created_at"]

    def __str__(self):
        return self.title
