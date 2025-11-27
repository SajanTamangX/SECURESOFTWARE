from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("instructor/", views.instructor_dashboard, name="instructor_dashboard"),
    path("test-404/", views.test_404, name="test_404"),  # Preview 404 page
    path("test-500/", views.test_500, name="test_500"),  # Preview 500 page
]

