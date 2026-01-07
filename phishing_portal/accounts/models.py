"""
User model for the Phishing Portal application.

This module extends Django's AbstractUser to add role-based access control.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    
    Adds role-based access control with three roles:
    - ADMIN: Full access to all features
    - INSTRUCTOR: Can create/manage campaigns and templates
    - VIEWER: Limited access, can only view their own data
    
    Inherits from AbstractUser, providing:
    - username, email, password fields
    - Authentication methods
    - Permission system
    """
    # User role choices for role-based access control (RBAC)
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"                    # Full administrative access
        INSTRUCTOR = "INSTRUCTOR", "Instructor"    # Can create/manage campaigns
        VIEWER = "VIEWER", "Viewer"                 # Limited read-only access

    # User role field - determines what features user can access
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,  # Default to VIEWER for security (least privilege)
    )

