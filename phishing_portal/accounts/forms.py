"""
Django forms for Accounts app.

This module defines form classes for user authentication.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    """
    Custom login form extending Django's AuthenticationForm.
    
    Adds Bootstrap styling classes for consistent UI.
    Includes username and password fields with placeholders.
    
    Security:
        - Inherits Django's built-in authentication validation
        - Password field uses PasswordInput widget (masks input)
        - CSRF protection handled by Django middleware
    """
    # Username field with Bootstrap styling
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    # Password field with Bootstrap styling and password masking
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

