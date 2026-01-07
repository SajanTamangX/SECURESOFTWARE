"""
Django admin configuration for Campaigns app models.

This module registers all campaign models with the Django admin interface,
providing a user-friendly way to manage campaigns, templates, recipients, etc.
"""

from django.contrib import admin
from .models import EmailTemplate, Campaign, Recipient, CampaignRecipient, Event, AuditLog, StickyNote


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """
    Admin interface for EmailTemplate model.
    
    Displays templates with name, subject, creator, and creation date.
    Allows filtering by creation date and searching by name/subject.
    """
    # Columns to display in list view
    list_display = ["name", "subject", "created_by", "created_at"]
    # Filters available in sidebar
    list_filter = ["created_at"]
    # Fields searchable in admin search box
    search_fields = ["name", "subject"]


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """
    Admin interface for Recipient model.
    
    Displays recipient email, name, and department.
    Allows searching by email or name.
    """
    list_display = ["email", "first_name", "last_name", "department"]
    search_fields = ["email", "first_name", "last_name"]


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """
    Admin interface for Campaign model.
    
    Displays campaign name, template, status, schedule, creator, and creation date.
    Allows filtering by status and date, searching by name/description.
    """
    list_display = ["name", "email_template", "status", "scheduled_for", "created_by", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["name", "description"]


@admin.register(CampaignRecipient)
class CampaignRecipientAdmin(admin.ModelAdmin):
    """
    Admin interface for CampaignRecipient model.
    
    Displays campaign-recipient links with tracking IDs and active status.
    Allows filtering by active status and date, searching by campaign/recipient.
    """
    list_display = ["campaign", "recipient", "tracking_id", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["campaign__name", "recipient__email"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin interface for Event model.
    
    Displays event type, recipient, timestamp, and user agent.
    Allows filtering by event type and date, searching by campaign/recipient.
    Creation timestamp is read-only.
    """
    list_display = ["campaign_recipient", "event_type", "created_at", "user_agent"]
    list_filter = ["event_type", "created_at"]
    search_fields = ["campaign_recipient__campaign__name", "campaign_recipient__recipient__email"]
    readonly_fields = ["created_at"]  # Prevent manual editing of timestamp


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Admin interface for AuditLog model.
    
    Displays audit log entries with timestamp, user, action, and IP hash.
    Allows filtering by date and action, searching by user/action/details.
    Includes date hierarchy for easy navigation by date.
    Creation timestamp is read-only.
    """
    list_display = ["created_at", "user", "action", "ip_address"]
    list_filter = ["created_at", "action"]
    search_fields = ["user__username", "action", "details"]
    readonly_fields = ["created_at"]  # Prevent manual editing of timestamp
    date_hierarchy = "created_at"  # Add date drill-down navigation


@admin.register(StickyNote)
class StickyNoteAdmin(admin.ModelAdmin):
    """
    Admin interface for StickyNote model.
    
    Displays note title, user, priority, completion status, and creation date.
    Allows filtering by priority, completion status, and date.
    Allows searching by title, body, or username.
    Creation timestamp is read-only.
    """
    list_display = ["title", "user", "priority", "is_done", "created_at"]
    list_filter = ["priority", "is_done", "created_at"]
    search_fields = ["title", "body", "user__username"]
    readonly_fields = ["created_at"]  # Prevent manual editing of timestamp
