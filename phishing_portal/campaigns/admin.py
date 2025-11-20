from django.contrib import admin
from .models import EmailTemplate, Campaign, Recipient, CampaignRecipient, Event, AuditLog, StickyNote


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "subject", "created_by", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "subject"]


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ["email", "first_name", "last_name", "department"]
    search_fields = ["email", "first_name", "last_name"]


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "email_template", "status", "scheduled_for", "created_by", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["name", "description"]


@admin.register(CampaignRecipient)
class CampaignRecipientAdmin(admin.ModelAdmin):
    list_display = ["campaign", "recipient", "tracking_id", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["campaign__name", "recipient__email"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["campaign_recipient", "event_type", "created_at", "user_agent"]
    list_filter = ["event_type", "created_at"]
    search_fields = ["campaign_recipient__campaign__name", "campaign_recipient__recipient__email"]
    readonly_fields = ["created_at"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["created_at", "user", "action", "ip_address"]
    list_filter = ["created_at", "action"]
    search_fields = ["user__username", "action", "details"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"


@admin.register(StickyNote)
class StickyNoteAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "priority", "is_done", "created_at"]
    list_filter = ["priority", "is_done", "created_at"]
    search_fields = ["title", "body", "user__username"]
    readonly_fields = ["created_at"]
