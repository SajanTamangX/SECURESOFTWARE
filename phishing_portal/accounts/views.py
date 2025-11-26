from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from .decorators import role_required


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "registration/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    template_name = "registration/logged_out.html"


@login_required
def home(request):
    # Get recent emails for the current user (if they have an email)
    # TODO: Maybe add pagination or "view all" link later
    recent_emails = []
    if request.user.email:
        from campaigns.models import CampaignEmail
        recent_emails = CampaignEmail.objects.filter(
            recipient__recipient__email=request.user.email
        ).select_related("campaign", "recipient", "recipient__recipient")[:5]  # Limit to 5 for now
    
    context = {
        "recent_emails": recent_emails,
    }
    return render(request, "home.html", context)


@role_required("ADMIN", "INSTRUCTOR")
def instructor_dashboard(request):
    return render(request, "instructor_dashboard.html", {
        "message": "Welcome to the Instructor Dashboard! Only Admins and Instructors can access this page."
    })

