"""
View functions for the Accounts app.

This module contains view functions for:
- User authentication (login, logout)
- Home page
- Role-based dashboards
- Custom error handlers (404, 500)
"""

from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, Http404
from django.contrib import messages
from .forms import LoginForm
from .decorators import role_required


class CustomLoginView(LoginView):
    """
    Custom login view extending Django's LoginView.
    
    Features:
    - Prevents information leakage (doesn't reveal if username exists)
    - Logs all login attempts (successful and failed)
    - Uses custom LoginForm with Bootstrap styling
    - Redirects authenticated users away from login page
    """
    form_class = LoginForm
    template_name = "registration/login.html"
    redirect_authenticated_user = True
    
    def form_invalid(self, form):
        """
        Override to prevent information leakage.
        Don't reveal whether username exists or password is wrong.
        """
        # Log failed login attempt (without sensitive data)
        from campaigns.utils import log_action
        username = form.data.get('username', 'unknown')[:50]  # Get from form.data, not cleaned_data
        # Only log if we have a request context (should always be true)
        if hasattr(self, 'request'):
            log_action(
                self.request,
                "Failed login attempt",
                f"Username: {username}"  # Truncate to prevent log injection
            )
        # Add generic error message that doesn't leak information
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)
    
    def form_valid(self, form):
        """Log successful login"""
        from campaigns.utils import log_action
        log_action(
            self.request,
            "Successful login",
            f"User: {form.get_user().username}"
        )
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    template_name = "registration/logged_out.html"


@login_required
def home(request):
    """
    Home page view showing recent emails for the current user.
    
    Displays the 5 most recent emails sent to the user's email address.
    Only shows emails if the user has an email address configured.
    
    Args:
        request: Django HttpRequest object
    
    Returns:
        HttpResponse: Rendered home.html template with recent emails
    """
    # Get recent emails for the current user (if they have an email)
    # TODO: Maybe add pagination or "view all" link later
    recent_emails = []
    if request.user.email:
        from campaigns.models import CampaignEmail
        # Filter emails sent to user's email address
        recent_emails = CampaignEmail.objects.filter(
            recipient__recipient__email=request.user.email
        ).select_related("campaign", "recipient", "recipient__recipient")[:5]  # Limit to 5 for now
    
    context = {
        "recent_emails": recent_emails,
    }
    return render(request, "home.html", context)


@role_required("ADMIN", "INSTRUCTOR")
def instructor_dashboard(request):
    """
    Instructor dashboard view (restricted to ADMIN and INSTRUCTOR roles).
    
    Displays instructor-specific dashboard with campaign management features.
    
    Args:
        request: Django HttpRequest object
    
    Returns:
        HttpResponse: Rendered instructor_dashboard.html template
    """
    return render(request, "instructor_dashboard.html", {
        "message": "Welcome to the Instructor Dashboard! Only Admins and Instructors can access this page."
    })


def custom_404_view(request, exception):
    """
    Custom 404 error handler.
    
    Shows a professional 404 error page instead of Django's default.
    
    Args:
        request: Django HttpRequest object
        exception: Exception that triggered 404
    
    Returns:
        HttpResponse: Rendered 404.html template with 404 status code
    """
    response = render(request, "404.html", {})
    response.status_code = 404
    return response


def custom_500_view(request):
    """
    Custom 500 error handler.
    
    Shows a professional 500 error page instead of Django's default.
    
    Args:
        request: Django HttpRequest object
    
    Returns:
        HttpResponse: Rendered 500.html template with 500 status code
    """
    response = render(request, "500.html", {})
    response.status_code = 500
    return response


def test_404(request):
    """Test view to preview the 404 page - visit /test-404/ to see it"""
    # Directly render the 404 template for preview (works even when DEBUG=True)
    response = render(request, "404.html", {})
    response.status_code = 404
    return response


def test_500(request):
    """Test view to preview the 500 page - visit /test-500/ to see it"""
    # Directly render the 500 template for preview (works even when DEBUG=True)
    response = render(request, "500.html", {})
    response.status_code = 500
    return response

