"""
URL configuration for phishing_portal project.
"""
from django.contrib import admin
from django.urls import path, include
from campaigns import views_admin, views_dashboard, views_export
from accounts import views as accounts_views

# Customize admin site
admin.site.site_header = "Phishing Portal Administration"
admin.site.site_title = "Phishing Portal Admin"
admin.site.index_title = "Welcome to Phishing Portal Administration"

urlpatterns = [
    path("", include("accounts.urls")),
    path("campaigns/", include("campaigns.urls")),
    path("dashboard/", views_dashboard.dashboard, name="dashboard"),
    path("audit/logs/", views_admin.audit_logs, name="audit_logs"),
    path("audit/logs/export/", views_export.export_audit_logs, name="export_audit_logs"),
    path("admin/", admin.site.urls),
]

# Custom error handlers
handler404 = accounts_views.custom_404_view
handler500 = accounts_views.custom_500_view

