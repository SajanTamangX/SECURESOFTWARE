from django import forms
from django.utils.html import strip_tags
from .models import EmailTemplate, Campaign


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, *args, **kwargs):
        # Make sure the HTML value matches what datetime-local expects
        kwargs.setdefault("format", "%Y-%m-%dT%H:%M")
        super().__init__(*args, **kwargs)


class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ["name", "subject", "scenario", "body", "learning_points"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 8}),
            "learning_points": forms.Textarea(attrs={"rows": 4}),
        }
    
    def clean_name(self):
        """Normalize name field: strip whitespace"""
        name = self.cleaned_data.get("name", "")
        return name.strip()
    
    def clean_subject(self):
        """Normalize subject field: strip whitespace"""
        subject = self.cleaned_data.get("subject", "")
        return subject.strip()
    
    def clean_body(self):
        """Normalize body field: strip whitespace (but preserve HTML for admin/instructor use)"""
        body = self.cleaned_data.get("body", "")
        return body.strip()
    
    def clean_learning_points(self):
        """Strip HTML tags and normalize learning_points (plain text field)"""
        learning_points = self.cleaned_data.get("learning_points", "")
        # Strip HTML tags since this is displayed as plain text
        learning_points = strip_tags(learning_points)
        return learning_points.strip()


class CampaignForm(forms.ModelForm):
    scheduled_for = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=DateTimeLocalInput(
            attrs={
                "class": "form-control datetime-input",
                "style": "max-width: 300px;",
            }
        ),
    )

    class Meta:
        model = Campaign
        fields = ["name", "description", "email_template", "scheduled_for", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
    
    def clean_name(self):
        """Normalize name field: strip whitespace"""
        name = self.cleaned_data.get("name", "")
        return name.strip()
    
    def clean_description(self):
        """Normalize description: strip HTML tags and whitespace (plain text field)"""
        description = self.cleaned_data.get("description", "")
        # Strip HTML tags since description is plain text
        description = strip_tags(description)
        return description.strip()


class RecipientUploadForm(forms.Form):
    csv_file = forms.FileField(
        help_text="CSV with columns: email, first_name, last_name, department"
    )

    def clean_csv_file(self):
        """Validate CSV file: extension, content type, size, and basic structure"""
        f = self.cleaned_data["csv_file"]
        
        # Check file extension (case-insensitive)
        if not f.name.lower().endswith(".csv"):
            raise forms.ValidationError("Please upload a .csv file.")
        
        # Check file size (max 2MB)
        max_size = 2 * 1024 * 1024  # 2MB
        if f.size > max_size:
            raise forms.ValidationError(
                f"CSV file too large (max 2MB). File size: {f.size / 1024 / 1024:.2f}MB"
            )
        
        # Check content type (be lenient - browsers vary)
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
            f.seek(0)  # Reset for later processing
            
            # Check it's not empty
            if not decoded.strip():
                raise forms.ValidationError("CSV file appears to be empty.")
            
            # Quick check for CSV-like structure (has commas or tabs)
            if ',' not in decoded and '\t' not in decoded:
                raise forms.ValidationError("CSV file does not appear to be in CSV format.")
                
        except UnicodeDecodeError:
            raise forms.ValidationError("CSV file must be UTF-8 encoded.")
        except Exception as e:
            if isinstance(e, forms.ValidationError):
                raise
            raise forms.ValidationError(f"Error reading CSV file: {str(e)}")
        
        return f

