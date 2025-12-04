from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import engines
from django.urls import reverse
from django.utils.html import strip_tags, escape

from .models import Campaign, CampaignRecipient, CampaignEmail, EmailTemplate

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
    Uses MailHog / configured SMTP backend in development.
    
    Note: In production, you'd want to use a task queue (Celery) for this.
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
