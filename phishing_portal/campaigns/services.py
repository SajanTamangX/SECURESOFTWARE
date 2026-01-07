"""
Service layer functions for Campaigns app.

This module contains business logic for:
- Email template rendering (scenario-based HTML email generation)
- Campaign email sending (sending emails to recipients)
- CSV recipient import (parsing and validating CSV files)

These functions are separated from views to:
- Improve code organization
- Enable reuse across different views
- Facilitate testing
- Follow separation of concerns principle
"""

import csv
import io

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from django.template import engines
from django.urls import reverse
from django.utils.html import strip_tags, escape
from django.db import transaction

from .models import Campaign, CampaignRecipient, CampaignEmail, EmailTemplate, Recipient

# Django template engine for rendering template strings
django_engine = engines["django"]


def render_body(template_body: str, context: dict) -> str:
    """Render template body with context - not currently used but kept for future"""
    tmpl = django_engine.from_string(template_body)
    return tmpl.render(context)


def _safe_name(ctx):
    """Get a safe name from context, fallback to 'Colleague' if nothing found"""
    return ctx.get("first_name") or ctx.get("full_name") or "Colleague"


def build_it_security_alert_body(email_template, ctx, click_url, report_url):
    recipient_name = _safe_name(ctx)
    html = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F3F4F6; font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
      <tr>
        <td align="center" style="padding:40px 20px;">
          <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,0.1); max-width:600px; border:1px solid #E5E7EB;">
            <!-- Header -->
            <tr>
              <td style="background-color:#F3F4F6; padding:24px 32px; border-bottom:1px solid #E5E7EB;">
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td>
                      <div style="color:#1F2937; font-size:18px; font-weight:600; margin-bottom:4px;">Indigo IT Security</div>
                      <div style="color:#6B7280; font-size:13px;">Security Notification</div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            
            <!-- Content -->
            <tr>
              <td style="padding:32px;">
                <p style="margin:0 0 20px 0; font-size:16px; line-height:22px; color:#1F2937;">Hi {recipient_name},</p>

                <p style="margin:0 0 20px 0; font-size:15px; line-height:22px; color:#1F2937;">
                  We detected a new sign-in to your <strong>Indigo Employee Portal</strong> account 
                  from a device or location we don't recognise.
                </p>

                <div style="background-color:#FEE2E2; border:1px solid #FCA5A5; padding:16px; margin:24px 0; border-radius:4px;">
                  <p style="margin:0; font-size:14px; line-height:20px; color:#991B1B;">
                    <strong>Important:</strong> If this was you, no further action is required. 
                    If this wasn't you, please review your recent activity immediately.
                  </p>
                </div>
                
                <table width="100%" cellpadding="0" cellspacing="0" style="margin:28px 0;">
                  <tr>
                    <td style="padding:12px 0;">
                      <a href="{click_url}" style="background-color:#2563EB; color:#FFFFFF; text-decoration:none; padding:12px 24px; border-radius:6px; font-weight:500; font-size:15px; display:inline-block;">
                        Review Account Activity
                      </a>
                    </td>
                  </tr>
                </table>
                
                <div style="border-top:1px solid #E5E7EB; margin-top:32px; padding-top:24px;">
                  <p style="margin:0 0 8px 0; font-size:14px; line-height:20px; color:#6B7280;">
                    Kind regards,<br>
                    <strong style="color:#1F2937;">Indigo IT Security Team</strong><br>
                    <a href="mailto:security@indigo.co.uk" style="color:#2563EB; text-decoration:none;">security@indigo.co.uk</a>
                  </p>
                </div>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    """
    text = strip_tags(html)
    return text, html


def build_password_reset_body(email_template, ctx, click_url, report_url):
    recipient_name = _safe_name(ctx)
    html = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F3F4F6; font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
      <tr>
        <td align="center" style="padding:40px 20px;">
          <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,0.1); max-width:600px; border:1px solid #E5E7EB;">
            <!-- Header -->
            <tr>
              <td style="background-color:#F3F4F6; padding:24px 32px; border-bottom:1px solid #E5E7EB;">
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td>
                      <div style="color:#1F2937; font-size:18px; font-weight:600; margin-bottom:4px;">Indigo Accounts</div>
                      <div style="color:#6B7280; font-size:13px;">Password Reset Request</div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            
            <!-- Content -->
            <tr>
              <td style="padding:32px;">
                <p style="margin:0 0 20px 0; font-size:16px; line-height:22px; color:#1F2937;">Hello {recipient_name},</p>

                <p style="margin:0 0 20px 0; font-size:15px; line-height:22px; color:#1F2937;">
                  A request was received to reset the password for your <strong>Indigo Single Sign-On</strong> account.
                </p>

                <p style="margin:0 0 24px 0; font-size:15px; line-height:22px; color:#1F2937;">
                  If you made this request, please confirm it by clicking the button below. This link will expire in 24 hours.
                </p>

                <table width="100%" cellpadding="0" cellspacing="0" style="margin:28px 0;">
                  <tr>
                    <td style="padding:12px 0;">
                      <a href="{click_url}" style="background-color:#2563EB; color:#FFFFFF; text-decoration:none; padding:12px 24px; border-radius:6px; font-weight:500; font-size:15px; display:inline-block;">
                        Confirm Password Reset
                      </a>
                    </td>
                  </tr>
                </table>
                
                <div style="background-color:#FEE2E2; border:1px solid #FCA5A5; padding:16px; margin:24px 0; border-radius:4px;">
                  <p style="margin:0; font-size:14px; line-height:20px; color:#991B1B;">
                    <strong>Important:</strong> If you did <strong>not</strong> make this request, please contact IT Support immediately 
                    and do not click the button above.
                  </p>
                </div>
                
                <div style="border-top:1px solid #E5E7EB; margin-top:32px; padding-top:24px;">
                  <p style="margin:0 0 8px 0; font-size:14px; line-height:20px; color:#6B7280;">
                    Best regards,<br>
                    <strong style="color:#1F2937;">Indigo IT Support Team</strong><br>
                    <a href="mailto:support@indigo.co.uk" style="color:#2563EB; text-decoration:none;">support@indigo.co.uk</a>
                  </p>
                </div>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    """
    text = strip_tags(html)
    return text, html


def build_payroll_body(email_template, ctx, click_url, report_url):
    recipient_name = _safe_name(ctx)
    html = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F3F4F6; font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
      <tr>
        <td align="center" style="padding:40px 20px;">
          <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,0.1); max-width:600px; border:1px solid #E5E7EB;">
            <!-- Header -->
            <tr>
              <td style="background-color:#F3F4F6; padding:24px 32px; border-bottom:1px solid #E5E7EB;">
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td>
                      <div style="color:#1F2937; font-size:18px; font-weight:600; margin-bottom:4px;">Indigo Payroll</div>
                      <div style="color:#6B7280; font-size:13px;">Payroll Update</div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            
            <!-- Content -->
            <tr>
              <td style="padding:32px;">
                <p style="margin:0 0 20px 0; font-size:16px; line-height:22px; color:#1F2937;">Dear {recipient_name},</p>

                <p style="margin:0 0 20px 0; font-size:15px; line-height:22px; color:#1F2937;">
                  As part of our end-of-month payroll checks, we were unable to automatically verify your current bank details.
                </p>

                <p style="margin:0 0 24px 0; font-size:15px; line-height:22px; color:#1F2937;">
                  To avoid any delay to your salary payment, please review and confirm your details in the Employee Payroll Portal.
                </p>

                <div style="background-color:#FEE2E2; border:1px solid #FCA5A5; padding:16px; margin:24px 0; border-radius:4px;">
                  <p style="margin:0; font-size:14px; line-height:20px; color:#991B1B;">
                    <strong>Important:</strong> Please complete this verification within 48 hours to ensure timely payment processing.
                  </p>
                </div>
                
                <table width="100%" cellpadding="0" cellspacing="0" style="margin:28px 0;">
                  <tr>
                    <td style="padding:12px 0;">
                      <a href="{click_url}" style="background-color:#2563EB; color:#FFFFFF; text-decoration:none; padding:12px 24px; border-radius:6px; font-weight:500; font-size:15px; display:inline-block;">
                        Review Payroll Details
                      </a>
                    </td>
                  </tr>
                </table>

                <p style="margin:24px 0 0 0; font-size:14px; line-height:20px; color:#6B7280;">
                  This verification should take less than two minutes to complete.
                </p>

                <div style="border-top:1px solid #E5E7EB; margin-top:32px; padding-top:24px;">
                  <p style="margin:0 0 8px 0; font-size:14px; line-height:20px; color:#6B7280;">
                    Best regards,<br>
                    <strong style="color:#1F2937;">Indigo Payroll Team</strong><br>
                    <a href="mailto:payroll@indigo.co.uk" style="color:#2563EB; text-decoration:none;">payroll@indigo.co.uk</a>
                  </p>
                </div>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    """
    text = strip_tags(html)
    return text, html


def build_delivery_failure_body(email_template, ctx, click_url, report_url):
    recipient_name = _safe_name(ctx)
    html = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F3F4F6; font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
      <tr>
        <td align="center" style="padding:40px 20px;">
          <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,0.1); max-width:600px; border:1px solid #E5E7EB;">
            <!-- Header -->
            <tr>
              <td style="background-color:#F3F4F6; padding:24px 32px; border-bottom:1px solid #E5E7EB;">
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td>
                      <div style="color:#1F2937; font-size:18px; font-weight:600; margin-bottom:4px;">Indigo Courier Service</div>
                      <div style="color:#6B7280; font-size:13px;">Delivery Notification</div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            
            <!-- Content -->
            <tr>
              <td style="padding:32px;">
                <p style="margin:0 0 20px 0; font-size:16px; line-height:22px; color:#1F2937;">Hi {recipient_name},</p>

                <p style="margin:0 0 20px 0; font-size:15px; line-height:22px; color:#1F2937;">
                  We attempted to deliver a package to your office address but were unable to complete the delivery.
                </p>

                <p style="margin:0 0 24px 0; font-size:15px; line-height:22px; color:#1F2937;">
                  Please confirm your delivery preferences so we can re-schedule the drop-off at your earliest convenience.
                </p>

                <div style="background-color:#FEE2E2; border:1px solid #FCA5A5; padding:16px; margin:24px 0; border-radius:4px;">
                  <p style="margin:0; font-size:14px; line-height:20px; color:#991B1B;">
                    <strong>Important:</strong> If no action is taken within 48 hours, your package may be returned to the sender.
                  </p>
                </div>
                
                <table width="100%" cellpadding="0" cellspacing="0" style="margin:28px 0;">
                  <tr>
                    <td style="padding:12px 0;">
                      <a href="{click_url}" style="background-color:#2563EB; color:#FFFFFF; text-decoration:none; padding:12px 24px; border-radius:6px; font-weight:500; font-size:15px; display:inline-block;">
                        Manage Delivery
                      </a>
                    </td>
                  </tr>
                </table>
                
                <div style="border-top:1px solid #E5E7EB; margin-top:32px; padding-top:24px;">
                  <p style="margin:0 0 8px 0; font-size:14px; line-height:20px; color:#6B7280;">
                    Best regards,<br>
                    <strong style="color:#1F2937;">Indigo Courier Service</strong><br>
                    <a href="mailto:courier@indigo.co.uk" style="color:#2563EB; text-decoration:none;">courier@indigo.co.uk</a>
                  </p>
                </div>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    """
    text = strip_tags(html)
    return text, html


def build_hr_policy_body(email_template, ctx, click_url, report_url):
    recipient_name = _safe_name(ctx)
    html = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F3F4F6; font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
      <tr>
        <td align="center" style="padding:40px 20px;">
          <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,0.1); max-width:600px; border:1px solid #E5E7EB;">
            <!-- Header -->
            <tr>
              <td style="background-color:#F3F4F6; padding:24px 32px; border-bottom:1px solid #E5E7EB;">
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td>
                      <div style="color:#1F2937; font-size:18px; font-weight:600; margin-bottom:4px;">Indigo People &amp; Culture</div>
                      <div style="color:#6B7280; font-size:13px;">Policy Update</div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            
            <!-- Content -->
            <tr>
              <td style="padding:32px;">
                <p style="margin:0 0 20px 0; font-size:16px; line-height:22px; color:#1F2937;">Dear {recipient_name},</p>

                <p style="margin:0 0 20px 0; font-size:15px; line-height:22px; color:#1F2937;">
                  We have recently updated our <strong>Employee Code of Conduct and Remote Working Policy</strong>. 
                  All staff are required to review and acknowledge the updated policy.
                </p>

                <div style="background-color:#FEE2E2; border:1px solid #FCA5A5; padding:16px; margin:24px 0; border-radius:4px;">
                  <p style="margin:0; font-size:14px; line-height:20px; color:#991B1B;">
                    <strong>Important:</strong> This acknowledgement is required and will form part of your employment record. 
                    Please complete this within 7 business days.
                  </p>
                </div>
                
                <table width="100%" cellpadding="0" cellspacing="0" style="margin:28px 0;">
                  <tr>
                    <td style="padding:12px 0;">
                      <a href="{click_url}" style="background-color:#2563EB; color:#FFFFFF; text-decoration:none; padding:12px 24px; border-radius:6px; font-weight:500; font-size:15px; display:inline-block;">
                        Review Policy &amp; Acknowledge
                      </a>
                    </td>
                  </tr>
                </table>
                
                <div style="border-top:1px solid #E5E7EB; margin-top:32px; padding-top:24px;">
                  <p style="margin:0 0 8px 0; font-size:14px; line-height:20px; color:#6B7280;">
                    Best regards,<br>
                    <strong style="color:#1F2937;">Indigo People &amp; Culture Team</strong><br>
                    <a href="mailto:hr@indigo.co.uk" style="color:#2563EB; text-decoration:none;">hr@indigo.co.uk</a>
                  </p>
                </div>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    """
    text = strip_tags(html)
    return text, html


def build_general_email_body(email_template, ctx, click_url, report_url):
    """
    Build a neutral, normal internal email layout.
    This is intentionally a normal, non-phishing message.
    """
    recipient_name = _safe_name(ctx)
    
    # Render the body text with context (supports placeholders like {{ first_name }})
    body_text = email_template.body or ""
    if body_text:
        body_rendered = render_body(body_text, ctx)
    else:
        body_rendered = ""
    
    # Convert line breaks to HTML paragraphs (escape HTML for safety)
    body_paragraphs = []
    for line in body_rendered.split('\n'):
        line = line.strip()
        if line:
            # Escape HTML entities to prevent XSS, then wrap in paragraph
            escaped_line = escape(line)
            body_paragraphs.append(f'<p style="margin:0 0 20px 0; font-size:15px; line-height:22px; color:#1F2937;">{escaped_line}</p>')
    
    body_html = '\n'.join(body_paragraphs) if body_paragraphs else '<p style="margin:0 0 20px 0; font-size:15px; line-height:22px; color:#1F2937;">&nbsp;</p>'
    
    html = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F3F4F6; font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
      <tr>
        <td align="center" style="padding:40px 20px;">
          <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,0.1); max-width:600px; border:1px solid #E5E7EB;">
            <!-- Header -->
            <tr>
              <td style="background-color:#F3F4F6; padding:24px 32px; border-bottom:1px solid #E5E7EB;">
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td>
                      <div style="color:#1F2937; font-size:18px; font-weight:600; margin-bottom:4px;">NepSoftware</div>
                      <div style="color:#6B7280; font-size:13px;">Internal Communication</div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            
            <!-- Content -->
            <tr>
              <td style="padding:32px;">
                {body_html}
                
                <div style="border-top:1px solid #E5E7EB; margin-top:32px; padding-top:24px;">
                  <p style="margin:0 0 8px 0; font-size:14px; line-height:20px; color:#6B7280;">
                    Kind regards,<br>
                    <strong style="color:#1F2937;">NepSoftware</strong>
                  </p>
                </div>
              </td>
            </tr>
            
            <!-- Footer -->
            <tr>
              <td style="background-color:#F3F4F6; padding:20px 32px; border-radius:0 0 6px 6px; border-top:1px solid #E5E7EB;">
                <p style="margin:0; font-size:12px; line-height:18px; color:#9CA3AF; text-align:left;">
                  This message was sent via the NepSoftware Security Portal.
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    """
    
    # Create plain text version
    text_body = strip_tags(body_rendered) if body_rendered else ""
    if text_body:
        # Preserve line breaks in plain text
        text_body = text_body.replace('\n', '\n\n')
    text_body += "\n\nKind regards,\nNepSoftware"
    
    return text_body, html


SCENARIO_BUILDERS = {
    EmailTemplate.Scenario.IT_ALERT: build_it_security_alert_body,
    EmailTemplate.Scenario.PASSWORD_RESET: build_password_reset_body,
    EmailTemplate.Scenario.PAYROLL: build_payroll_body,
    EmailTemplate.Scenario.DELIVERY: build_delivery_failure_body,
    EmailTemplate.Scenario.HR_POLICY: build_hr_policy_body,
    EmailTemplate.Scenario.GENERAL: build_general_email_body,
}


def send_campaign_emails(campaign: Campaign, request=None):
    """
    Send emails for a campaign to all linked recipients.
    
    This function:
    1. Iterates through all CampaignRecipient links for the campaign
    2. Renders email body using scenario-specific template builders
    3. Adds tracking URLs (open, click, report)
    4. Sends email via Django's email backend (MailHog in dev, SMTP in prod)
    5. Creates CampaignEmail records for inbox feature
    
    Args:
        campaign: Campaign instance to send emails for
        request: Optional HttpRequest object (used to build absolute URLs)
    
    Note: In production, you'd want to use a task queue (Celery) for this
    to avoid blocking the web request and handle large campaigns.
    """
    cr_qs = CampaignRecipient.objects.select_related("recipient").filter(campaign=campaign)
    
    for cr in cr_qs:
        rec = cr.recipient
        
        subject = campaign.email_template.subject

        # Context for placeholders
        ctx = {
            "first_name": rec.first_name or "",
            "full_name": f"{rec.first_name} {rec.last_name}".strip() if rec.first_name or rec.last_name else "",
            "email": rec.email,
            "campaign": campaign,
        }

        # URLs for tracking
        tracking_id = str(cr.tracking_id)
        click_url = reverse("campaigns:track_click", kwargs={"tracking_id": tracking_id})
        report_url = reverse("campaigns:track_report", kwargs={"tracking_id": tracking_id})
        open_url = reverse("campaigns:track_open", kwargs={"tracking_id": tracking_id})
        
        if request is not None:
            base = request.build_absolute_uri("/")
            base = base.rstrip("/")
            open_url = base + open_url
            click_url = base + click_url
            report_url = base + report_url

        # Choose builder function based on template scenario
        tpl = campaign.email_template
        builder = SCENARIO_BUILDERS.get(tpl.scenario, build_it_security_alert_body)  # Default fallback

        text_main, html_main = builder(tpl, ctx, click_url, report_url)

        # Append a generic footer to text version (skip for GENERAL emails)
        if tpl.scenario == EmailTemplate.Scenario.GENERAL:
            body_text = text_main
        else:
            body_text = text_main + (
                "\n\nIf you did not expect this message, please contact IT Support "
                f"or report it here: {report_url}\n"
            )

        # Wrap HTML and add tracking pixel
        html_body = f"""
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
          </head>
          <body style="margin:0; padding:0; background-color:#f5f7fa; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
            {html_main}
            <img src="{open_url}" width="1" height="1"
                 style="display:none; width:1px; height:1px; border:none;" alt="" />
          </body>
        </html>
        """

        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
            to=[rec.email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()

        CampaignEmail.objects.create(
            campaign=campaign,
            recipient=cr,
            subject=subject,
            body_text=body_text,
            body_html=html_body,
        )


def import_recipients_from_csv(uploaded_file, campaign, user, log_action_func=None):
    """
    Import recipients from CSV file with robust validation and error handling.
    
    This function:
    1. Validates CSV structure and encoding (UTF-8)
    2. Validates required columns (email)
    3. Validates email format for each row
    4. Checks for duplicates within the file
    5. Creates Recipient objects (or gets existing ones)
    6. Links recipients to campaign via CampaignRecipient
    7. Returns detailed results including errors
    
    Security features:
    - Input validation and sanitization
    - Email format validation
    - Duplicate detection
    - Row limit enforcement (1000 max)
    - Transaction rollback on critical errors
    - Detailed error reporting
    
    Args:
        uploaded_file: Django UploadedFile object (already validated for extension/size)
        campaign: Campaign instance to link recipients to
        user: User instance for logging
        log_action_func: Optional function to log actions (from campaigns.utils.log_action)
    
    Returns:
        tuple: (created_count, linked_count, error_rows, error_details)
        - created_count: Number of new Recipient objects created
        - linked_count: Number of CampaignRecipient links created
        - error_rows: List of row numbers that had errors
        - error_details: Dict mapping row numbers to error messages
    
    Raises:
        ValueError: If CSV structure is invalid, encoding is wrong, or limit exceeded
    """
    MAX_RECIPIENTS = 1000
    
    created_count = 0
    linked_count = 0
    error_rows = []
    error_details = {}
    
    try:
        # Read and decode file
        decoded = uploaded_file.read().decode("utf-8")
        uploaded_file.seek(0)  # Reset for potential re-reading
        reader = csv.DictReader(io.StringIO(decoded))
        
        # Validate required columns
        required_columns = {"email"}
        if not reader.fieldnames:
            raise ValueError("CSV file appears to be empty or invalid.")
        
        missing_columns = required_columns - set(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Track emails to detect duplicates within the file
        emails_seen_in_file = set()
        row_num = 1  # Start at 1 (header is row 0)
        
        # Process rows in a transaction for atomicity
        with transaction.atomic():
            for row in reader:
                row_num += 1
                row_errors = []
                
                # Extract and normalize fields
                email = row.get("email", "").strip()
                first_name = row.get("first_name", "").strip()
                last_name = row.get("last_name", "").strip()
                department = row.get("department", "").strip()
                
                # Validate email is present
                if not email:
                    row_errors.append("Email is required")
                    error_rows.append(row_num)
                    error_details[row_num] = "Email is required"
                    continue
                
                # Validate email format
                try:
                    validate_email(email)
                except DjangoValidationError:
                    row_errors.append(f"Invalid email format: {email}")
                    error_rows.append(row_num)
                    error_details[row_num] = f"Invalid email format: {email}"
                    continue
                
                # Check for duplicates within the file
                email_lower = email.lower()
                if email_lower in emails_seen_in_file:
                    row_errors.append(f"Duplicate email in file: {email}")
                    error_rows.append(row_num)
                    error_details[row_num] = f"Duplicate email in file: {email}"
                    continue
                emails_seen_in_file.add(email_lower)
                
                # Check recipient limit before processing
                if created_count + linked_count >= MAX_RECIPIENTS:
                    if log_action_func:
                        log_action_func(
                            None,
                            "Recipient limit exceeded - CSV upload",
                            f"User: {user.username}, Campaign: {campaign.name} (ID: {campaign.id}), "
                            f"Limit: {MAX_RECIPIENTS}, Processed: {created_count + linked_count}"
                        )
                    raise ValueError("Recipient limit exceeded: Maximum 1000 recipients allowed per upload.")
                
                # Create or get recipient
                try:
                    recipient, created = Recipient.objects.get_or_create(
                        email=email_lower,  # Use lowercase for consistency
                        defaults={
                            "first_name": first_name[:100] if first_name else "",  # Enforce max_length
                            "last_name": last_name[:100] if last_name else "",  # Enforce max_length
                            "department": department[:100] if department else "",  # Enforce max_length
                        },
                    )
                    
                    if created:
                        created_count += 1
                    
                    # Link to campaign (ignore if already linked)
                    _, link_created = CampaignRecipient.objects.get_or_create(
                        campaign=campaign,
                        recipient=recipient,
                    )
                    
                    if link_created:
                        linked_count += 1
                        
                except Exception as e:
                    # Database-level errors (e.g., constraint violations)
                    error_rows.append(row_num)
                    error_details[row_num] = f"Database error: {str(e)}"
                    continue
        
        # Log suspicious activity if many errors
        if len(error_rows) > 10 and log_action_func:
            # log_action_func expects (request, action, details) signature
            # Pass None for request - the logging function should handle it
            log_action_func(
                None,  # Request object not available in service layer
                "Suspicious CSV import - many errors",
                f"User: {user.username}, Campaign: {campaign.name} (ID: {campaign.id}), "
                f"Errors: {len(error_rows)}/{row_num - 1} rows"
            )
        
        # Check if file had any data rows
        if row_num == 1:  # Only header row
            raise ValueError("CSV file contains no data rows.")
        
    except UnicodeDecodeError:
        raise ValueError("CSV file must be UTF-8 encoded.")
    except csv.Error as e:
        raise ValueError(f"Invalid CSV format: {str(e)}")
    except Exception as e:
        # Re-raise ValueError, wrap others
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Error processing CSV file: {str(e)}")
    
    return created_count, linked_count, error_rows, error_details
