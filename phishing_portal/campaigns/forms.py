from django import forms
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


class RecipientUploadForm(forms.Form):
    csv_file = forms.FileField(
        help_text="CSV with columns: email, first_name, last_name, department"
    )

    def clean_csv_file(self):
        import csv
        import io
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError as DjangoValidationError
        
        f = self.cleaned_data["csv_file"]
        if not f.name.lower().endswith(".csv"):
            raise forms.ValidationError("Please upload a .csv file.")
        if f.size > 2 * 1024 * 1024:
            raise forms.ValidationError("CSV file too large (max 2MB).")
        
        # Read and validate CSV content
        try:
            decoded = f.read().decode("utf-8")
            f.seek(0)  # Reset file pointer
            reader = csv.DictReader(io.StringIO(decoded))
            
            # Check required columns
            required_columns = {"email"}
            if not reader.fieldnames:
                raise forms.ValidationError("CSV file appears to be empty or invalid.")
            
            missing_columns = required_columns - set(reader.fieldnames or [])
            if missing_columns:
                raise forms.ValidationError(
                    f"Missing required columns: {', '.join(missing_columns)}"
                )
            
            # Validate email format and check for duplicates
            emails_seen = set()
            row_num = 1  # Header is row 0, data starts at 1
            
            for row in reader:
                row_num += 1
                email = row.get("email", "").strip()
                
                if not email:
                    raise forms.ValidationError(
                        f"Row {row_num}: Email is required."
                    )
                
                # Validate email format
                try:
                    validate_email(email)
                except DjangoValidationError:
                    raise forms.ValidationError(
                        f"Row {row_num}: Invalid email format: {email}"
                    )
                
                # Check for duplicates
                if email.lower() in emails_seen:
                    raise forms.ValidationError(
                        f"Row {row_num}: Duplicate email found: {email}"
                    )
                emails_seen.add(email.lower())
            
            if row_num == 1:  # Only header row
                raise forms.ValidationError("CSV file contains no data rows.")
                
        except UnicodeDecodeError:
            raise forms.ValidationError("CSV file must be UTF-8 encoded.")
        except csv.Error as e:
            raise forms.ValidationError(f"Invalid CSV format: {str(e)}")
        except Exception as e:
            if isinstance(e, forms.ValidationError):
                raise
            raise forms.ValidationError(f"Error reading CSV file: {str(e)}")
        
        return f

