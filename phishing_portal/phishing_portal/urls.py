"""
URL configuration for phishing_portal project.
"""
from django.contrib import admin
from django.urls import path, include
from campaigns import views_admin, views_dashboard, views_export

urlpatterns = [
    path("", include("accounts.urls")),
    path("campaigns/", include("campaigns.urls")),
    path("dashboard/", views_dashboard.dashboard, name="dashboard"),
    path("audit/logs/", views_admin.audit_logs, name="audit_logs"),
    path("audit/logs/export/", views_export.export_audit_logs, name="export_audit_logs"),
    path("admin/", admin.site.urls),
]

