"""
URL configuration for Accounts app.

This module defines URL patterns for:
- User authentication (login, logout)
- Home page
- Role-based dashboards
- Error page previews (for testing)
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home page (requires login)
    path("", views.home, name="home"),
    # User authentication URLs
    path("login/", views.CustomLoginView.as_view(), name="login"),      # Login page
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),   # Logout page
    # Instructor dashboard (restricted to ADMIN/INSTRUCTOR roles)
    path("instructor/", views.instructor_dashboard, name="instructor_dashboard"),
    # Test URLs for previewing error pages (useful for development/testing)
    path("test-404/", views.test_404, name="test_404"),  # Preview 404 page
    path("test-500/", views.test_500, name="test_500"),  # Preview 500 page
]

