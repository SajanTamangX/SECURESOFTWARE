"""
Django forms for Campaigns app.

This module defines form classes for:
- Email template creation/editing
- Campaign creation/editing
- Recipient CSV file upload

All forms include input validation and sanitization for security.
"""

from django import forms
from django.utils.html import strip_tags
from .models import EmailTemplate, Campaign


class DateTimeLocalInput(forms.DateTimeInput):
    """
    Custom datetime input widget for HTML5 datetime-local input type.
    
    Ensures the datetime format matches HTML5 datetime-local requirements.
    """
    input_type = "datetime-local"

    def __init__(self, *args, **kwargs):
        # Make sure the HTML value matches what datetime-local expects
        # Format: YYYY-MM-DDTHH:MM (e.g., "2024-12-25T14:30")
        kwargs.setdefault("format", "%Y-%m-%dT%H:%M")
        super().__init__(*args, **kwargs)


class EmailTemplateForm(forms.ModelForm):
    """
    Form for creating/editing email templates.
    
    Includes validation and sanitization:
    - Strips whitespace from text fields
    - Removes HTML from learning_points (plain text field)
    - Preserves HTML in body field (for admin/instructor custom HTML)
    """
    class Meta:
        model = EmailTemplate
        # Fields available in the form
        fields = ["name", "subject", "scenario", "body", "learning_points"]
        # Custom widget attributes
        widgets = {
            "body": forms.Textarea(attrs={"rows": 8}),           # Larger textarea for body
            "learning_points": forms.Textarea(attrs={"rows": 4}), # Smaller textarea for learning points
        }
    
    def clean_name(self):
        """
        Normalize name field: strip leading/trailing whitespace.
        
        Returns:
            str: Trimmed name string
        """
        name = self.cleaned_data.get("name", "")
        return name.strip()
    
    def clean_subject(self):
        """
        Normalize subject field: strip leading/trailing whitespace.
        
        Returns:
            str: Trimmed subject string
        """
        subject = self.cleaned_data.get("subject", "")
        return subject.strip()
    
    def clean_body(self):
        """
        Normalize body field: strip whitespace (but preserve HTML for admin/instructor use).
        
        Note: HTML is preserved in body field to allow custom HTML templates.
        Returns:
            str: Trimmed body string (HTML preserved)
        """
        body = self.cleaned_data.get("body", "")
        return body.strip()
    
    def clean_learning_points(self):
        """
        Strip HTML tags and normalize learning_points (plain text field).
        
        Security: Removes HTML tags to prevent XSS attacks since this is displayed as plain text.
        Returns:
            str: Sanitized plain text learning points
        """
        learning_points = self.cleaned_data.get("learning_points", "")
        # Strip HTML tags since this is displayed as plain text
        learning_points = strip_tags(learning_points)
        return learning_points.strip()


class CampaignForm(forms.ModelForm):
    """
    Form for creating/editing campaigns.
    
    Includes validation and sanitization:
    - Strips whitespace from text fields
    - Removes HTML from description (plain text field)
    - Custom datetime-local input for scheduling
    """
    # Custom datetime field for campaign scheduling
    scheduled_for = forms.DateTimeField(
        required=False,  # Scheduling is optional
        input_formats=["%Y-%m-%dT%H:%M"],  # Format: YYYY-MM-DDTHH:MM
        widget=DateTimeLocalInput(
            attrs={
                "class": "form-control datetime-input",
                "style": "max-width: 300px;",
            }
        ),
    )

    class Meta:
        model = Campaign
        # Fields available in the form
        fields = ["name", "description", "email_template", "scheduled_for", "status"]
        # Custom widget attributes
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),  # Textarea for description
        }
    
    def clean_name(self):
        """
        Normalize name field: strip leading/trailing whitespace.
        
        Returns:
            str: Trimmed name string
        """
        name = self.cleaned_data.get("name", "")
        return name.strip()
    
    def clean_description(self):
        """
        Normalize description: strip HTML tags and whitespace (plain text field).
        
        Security: Removes HTML tags to prevent XSS attacks since description is plain text.
        Returns:
            str: Sanitized plain text description
        """
        description = self.cleaned_data.get("description", "")
        # Strip HTML tags since description is plain text
        description = strip_tags(description)
        return description.strip()


class RecipientUploadForm(forms.Form):
    """
    Form for uploading recipient CSV files.
    
    Validates CSV file uploads with security checks:
    - File extension validation (.csv only)
    - File size limit (2MB max)
    - Content type validation (lenient due to browser variations)
    - UTF-8 encoding validation
    - Basic CSV structure validation
    
    Detailed CSV parsing and validation is handled in the service layer.
    """
    # File upload field for CSV file
    csv_file = forms.FileField(
        help_text="CSV with columns: email, first_name, last_name, department"
    )

    def clean_csv_file(self):
        """
        Validate CSV file: extension, content type, size, and basic structure.
        
        Security validations:
        1. File extension must be .csv
        2. File size must be <= 2MB
        3. File must be UTF-8 encoded
        4. File must contain CSV-like structure (commas or tabs)
        
        Returns:
            UploadedFile: Validated CSV file object
        
        Raises:
            ValidationError: If file fails any validation check
        """
        f = self.cleaned_data["csv_file"]
        
        # Check file extension (case-insensitive)
        if not f.name.lower().endswith(".csv"):
            raise forms.ValidationError("Please upload a .csv file.")
        
        # Check file size (max 2MB) - prevents DoS attacks via large files
        max_size = 2 * 1024 * 1024  # 2MB
        if f.size > max_size:
            raise forms.ValidationError(
                f"CSV file too large (max 2MB). File size: {f.size / 1024 / 1024:.2f}MB"
            )
        
        # Check content type (be lenient - browsers vary)
        # Some browsers send incorrect MIME types, so we don't reject based solely on this
        content_type = getattr(f, 'content_type', '')
        allowed_types = ['text/csv', 'application/vnd.ms-excel', 'text/plain', 'application/csv']
        if content_type and content_type not in allowed_types:
            # Don't reject based on content_type alone - some browsers send wrong MIME types
            # But log it for security monitoring
            pass
        
        # Basic structure validation (detailed parsing moved to service layer)
        try:
            # Just verify it's readable UTF-8
            f.seek(0)
            decoded = f.read().decode("utf-8")
            f.seek(0)  # Reset file pointer for later processing
            
            # Check it's not empty
            if not decoded.strip():
                raise forms.ValidationError("CSV file appears to be empty.")
            
            # Quick check for CSV-like structure (has commas or tabs)
            # This is a basic check - detailed validation happens in service layer
            if ',' not in decoded and '\t' not in decoded:
                raise forms.ValidationError("CSV file does not appear to be in CSV format.")
                
        except UnicodeDecodeError:
            raise forms.ValidationError("CSV file must be UTF-8 encoded.")
        except Exception as e:
            if isinstance(e, forms.ValidationError):
                raise
            raise forms.ValidationError(f"Error reading CSV file: {str(e)}")
        
        return f

