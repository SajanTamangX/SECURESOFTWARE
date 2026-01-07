"""
URL configuration for phishing_portal project.

This is the root URL configuration that includes:
- Account URLs (login, logout, home)
- Campaign URLs (campaigns, templates, tracking)
- Dashboard URLs
- Audit log URLs
- Django admin URLs
- Custom error handlers (404, 500)
"""

from django.contrib import admin
from django.urls import path, include
from campaigns import views_admin, views_dashboard, views_export
from accounts import views as accounts_views

# Customize Django admin site branding
admin.site.site_header = "Phishing Portal Administration"
admin.site.site_title = "Phishing Portal Admin"
admin.site.index_title = "Welcome to Phishing Portal Administration"

# Root URL patterns
urlpatterns = [
    # Account URLs (login, logout, home page)
    path("", include("accounts.urls")),
    # Campaign URLs (campaigns, templates, tracking, inbox, etc.)
    path("campaigns/", include("campaigns.urls")),
    # Dashboard URL (main dashboard view)
    path("dashboard/", views_dashboard.dashboard, name="dashboard"),
    # Audit log URLs (view and export audit logs)
    path("audit/logs/", views_admin.audit_logs, name="audit_logs"),
    path("audit/logs/export/", views_export.export_audit_logs, name="export_audit_logs"),
    # Django admin interface
    path("admin/", admin.site.urls),
]

# Custom error handlers for professional error pages
# These override Django's default error handlers
handler404 = accounts_views.custom_404_view  # Custom 404 page
handler500 = accounts_views.custom_500_view  # Custom 500 page

