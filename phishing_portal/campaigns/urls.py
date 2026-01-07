"""
URL configuration for Campaigns app.

This module defines all URL patterns for the campaigns application,
including campaign management, email templates, tracking, and user features.
"""

from django.urls import path
from . import views, views_export

# App namespace for URL reversing (e.g., campaigns:campaign_list)
app_name = "campaigns"

urlpatterns = [
    # Email Template URLs
    path("templates/", views.template_list, name="template_list"),           # List all email templates
    path("templates/new/", views.template_create, name="template_create"),     # Create new email template
    
    # Campaign URLs
    path("", views.campaign_list, name="campaign_list"),                       # List all campaigns
    path("new/", views.campaign_create, name="campaign_create"),               # Create new campaign
    path("<int:pk>/", views.campaign_detail, name="campaign_detail"),         # View campaign details
    path("<int:pk>/upload-recipients/", views.upload_recipients, name="upload_recipients"),  # Upload recipients CSV
    path("<int:pk>/send/", views.send_campaign, name="send_campaign"),         # Send campaign emails
    
    # Export URLs
    path("<int:pk>/export-recipients/", views_export.export_campaign_recipients, name="export_recipients"),  # Export recipients CSV
    path("<int:pk>/export-events/", views_export.export_campaign_events, name="export_events"),            # Export events CSV
    
    # Email Tracking URLs (used in phishing emails)
    path("t/<uuid:tracking_id>/open/", views.track_open, name="track_open"),    # Track email open (1x1 pixel)
    path("t/<uuid:tracking_id>/click/", views.track_click, name="track_click"), # Track link click
    path("t/<uuid:tracking_id>/report/", views.track_report, name="track_report"), # Track phishing report
    path("l/<uuid:tracking_id>/", views.landing_page, name="landing_page"),   # Landing page after click
    
    # Inbox URLs (for viewing received emails)
    path("inbox/", views.inbox, name="inbox"),                                 # List emails in inbox
    path("inbox/<int:pk>/", views.inbox_detail, name="inbox_detail"),          # View email details
    path("inbox/<int:pk>/toggle-read/", views.toggle_email_read, name="toggle_email_read"),  # Toggle read status
    
    # Blog URLs (educational content for all roles)
    path("<str:role>/blog/", views.blog_list, name="blog_list"),               # List blog posts by role
    path("<str:role>/blog/<slug:slug>/", views.blog_detail, name="blog_detail"), # View blog post detail
    
    # Viewer-specific URLs
    path("viewer/notes/", views.viewer_notes_board, name="viewer_notes_board"), # Sticky notes board
    path("viewer/notes/<int:note_id>/toggle/", views.viewer_note_toggle, name="viewer_note_toggle"), # Toggle note completion
    
    # Training URLs
    path("training/videos/", views.training_videos, name="training_videos"),     # Training videos page
]

