from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import engines
from django.urls import reverse
from django.utils.html import strip_tags

from .models import Campaign, CampaignRecipient, CampaignEmail, EmailTemplate

django_engine = engines["django"]


def render_body(template_body: str, context: dict) -> str:
    tmpl = django_engine.from_string(template_body)
    return tmpl.render(context)


def _safe_name(ctx):
    return ctx.get("first_name") or ctx.get("full_name") or "Colleague"


def build_it_security_alert_body(email_template, ctx, click_url, report_url):
    recipient_name = _safe_name(ctx)
    html = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7fa; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
      <tr>
        <td align="center" style="padding:40px 20px;">
          <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.08); max-width:600px;">
            <!-- Header -->
            <tr>
              <td style="background:linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding:24px 32px; border-radius:8px 8px 0 0;">
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td>
                      <div style="color:#ffffff; font-size:20px; font-weight:600; letter-spacing:-0.5px;">Indigo IT Security</div>
                      <div style="color:rgba(255,255,255,0.9); font-size:13px; margin-top:4px;">Security Operations Center</div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            
            <!-- Content -->
            <tr>
              <td style="padding:32px;">
                <p style="margin:0 0 16px 0; font-size:16px; line-height:24px; color:#1f2937;">Hi {recipient_name},</p>

                <p style="margin:0 0 20px 0; font-size:15px; line-height:24px; color:#374151;">
                  We detected a new sign-in to your <strong style="color:#1f2937;">Indigo Employee Portal</strong> account 
        from a device or location we don't recognise.
      </p>

                <div style="background-color:#fef3c7; border-left:4px solid #f59e0b; padding:16px; margin:24px 0; border-radius:4px;">
                  <p style="margin:0; font-size:14px; line-height:20px; color:#92400e;">
                    <strong>Security Alert:</strong> If this was you, no further action is required. 
                    If this wasn't you, please review your recent activity immediately.
      </p>
                </div>
                
                <table width="100%" cellpadding="0" cellspacing="0" style="margin:28px 0;">
                  <tr>
                    <td align="center" style="padding:12px 0;">
                      <a href="{click_url}" style="background-color:#2563eb; color:#ffffff; text-decoration:none; padding:14px 32px; border-radius:6px; font-weight:600; font-size:15px; display:inline-block; box-shadow:0 2px 4px rgba(37,99,235,0.3);">
          Review Account Activity
        </a>
                    </td>
                  </tr>
                </table>
                
                <div style="border-top:1px solid #e5e7eb; margin-top:32px; padding-top:24px;">
                  <p style="margin:0 0 8px 0; font-size:14px; line-height:20px; color:#6b7280;">
                    Kind regards,<br>
                    <strong style="color:#1f2937;">Indigo IT Security Team</strong><br>
                    <a href="mailto:security@indigo.co.uk" style="color:#2563eb; text-decoration:none;">security@indigo.co.uk</a>
                  </p>
                </div>
              </td>
            </tr>
            
            <!-- Footer -->
            <tr>
              <td style="background-color:#f9fafb; padding:20px 32px; border-radius:0 0 8px 8px; border-top:1px solid #e5e7eb;">
                <p style="margin:0; font-size:12px; line-height:18px; color:#6b7280; text-align:center;">
                  This is an automated security notification from Indigo IT Security.<br>
                  If you have concerns, contact IT Support directly.
                </p>
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
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7fa; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
      <tr>
        <td align="center" style="padding:40px 20px;">
          <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.08); max-width:600px;">
            <!-- Header -->
            <tr>
              <td style="background:linear-gradient(135deg, #7c3aed 0%, #a855f7 100%); padding:24px 32px; border-radius:8px 8px 0 0;">
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td>
                      <div style="color:#ffffff; font-size:20px; font-weight:600; letter-spacing:-0.5px;">Indigo Accounts</div>
                      <div style="color:rgba(255,255,255,0.9); font-size:13px; margin-top:4px;">Single Sign-On Portal</div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            
            <!-- Content -->
            <tr>
              <td style="padding:32px;">
                <p style="margin:0 0 16px 0; font-size:16px; line-height:24px; color:#1f2937;">Hello {recipient_name},</p>

                <p style="margin:0 0 20px 0; font-size:15px; line-height:24px; color:#374151;">
                  A request was received to reset the password for your <strong style="color:#1f2937;">Indigo Single Sign-On</strong> account.
      </p>

                <p style="margin:0 0 24px 0; font-size:15px; line-height:24px; color:#374151;">
                  If you made this request, please confirm it by clicking the button below. This link will expire in 24 hours.
      </p>

                <table width="100%" cellpadding="0" cellspacing="0" style="margin:28px 0;">
                  <tr>
                    <td align="center" style="padding:12px 0;">
                      <a href="{click_url}" style="background-color:#7c3aed; color:#ffffff; text-decoration:none; padding:14px 32px; border-radius:6px; font-weight:600; font-size:15px; display:inline-block; box-shadow:0 2px 4px rgba(124,58,237,0.3);">
          Confirm Password Reset
        </a>
                    </td>
                  </tr>
                </table>
                
                <div style="background-color:#fee2e2; border-left:4px solid #ef4444; padding:16px; margin:24px 0; border-radius:4px;">
                  <p style="margin:0; font-size:14px; line-height:20px; color:#991b1b;">
                    <strong>Important:</strong> If you did <strong>not</strong> make this request, please contact IT Support immediately 
                    and do not click the button above.
                  </p>
                </div>
                
                <div style="border-top:1px solid #e5e7eb; margin-top:32px; padding-top:24px;">
                  <p style="margin:0 0 8px 0; font-size:14px; line-height:20px; color:#6b7280;">
                    Best regards,<br>
                    <strong style="color:#1f2937;">Indigo IT Support Team</strong><br>
                    <a href="mailto:support@indigo.co.uk" style="color:#7c3aed; text-decoration:none;">support@indigo.co.uk</a>
      </p>
                </div>
              </td>
            </tr>
            
            <!-- Footer -->
            <tr>
              <td style="background-color:#f9fafb; padding:20px 32px; border-radius:0 0 8px 8px; border-top:1px solid #e5e7eb;">
                <p style="margin:0; font-size:12px; line-height:18px; color:#6b7280; text-align:center;">
                  This password reset link expires in 24 hours for security purposes.<br>
                  If you didn't request this, please contact IT Support immediately.
      </p>
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
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7fa; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
      <tr>
        <td align="center" style="padding:40px 20px;">
          <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.08); max-width:600px;">
            <!-- Header -->
            <tr>
              <td style="background:linear-gradient(135deg, #059669 0%, #10b981 100%); padding:24px 32px; border-radius:8px 8px 0 0;">
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td>
                      <div style="color:#ffffff; font-size:20px; font-weight:600; letter-spacing:-0.5px;">Indigo Payroll</div>
                      <div style="color:rgba(255,255,255,0.9); font-size:13px; margin-top:4px;">Human Resources & Finance</div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            
            <!-- Content -->
            <tr>
              <td style="padding:32px;">
                <p style="margin:0 0 16px 0; font-size:16px; line-height:24px; color:#1f2937;">Dear {recipient_name},</p>

                <p style="margin:0 0 20px 0; font-size:15px; line-height:24px; color:#374151;">
                  As part of our end-of-month payroll checks, we were unable to automatically verify your current bank details.
      </p>

                <p style="margin:0 0 24px 0; font-size:15px; line-height:24px; color:#374151;">
                  To avoid any delay to your salary payment, please review and confirm your details in the Employee Payroll Portal.
      </p>

                <div style="background-color:#d1fae5; border-left:4px solid #10b981; padding:16px; margin:24px 0; border-radius:4px;">
                  <p style="margin:0; font-size:14px; line-height:20px; color:#065f46;">
                    <strong>Action Required:</strong> Please complete this verification within 48 hours to ensure timely payment processing.
                  </p>
                </div>
                
                <table width="100%" cellpadding="0" cellspacing="0" style="margin:28px 0;">
                  <tr>
                    <td align="center" style="padding:12px 0;">
                      <a href="{click_url}" style="background-color:#059669; color:#ffffff; text-decoration:none; padding:14px 32px; border-radius:6px; font-weight:600; font-size:15px; display:inline-block; box-shadow:0 2px 4px rgba(5,150,105,0.3);">
          Review Payroll Details
        </a>
                    </td>
                  </tr>
                </table>

                <p style="margin:24px 0 0 0; font-size:14px; line-height:20px; color:#6b7280;">
        This verification should take less than two minutes to complete.
      </p>

                <div style="border-top:1px solid #e5e7eb; margin-top:32px; padding-top:24px;">
                  <p style="margin:0 0 8px 0; font-size:14px; line-height:20px; color:#6b7280;">
                    Best regards,<br>
                    <strong style="color:#1f2937;">Indigo Payroll Team</strong><br>
                    <a href="mailto:payroll@indigo.co.uk" style="color:#059669; text-decoration:none;">payroll@indigo.co.uk</a>
                  </p>
    </div>
              </td>
            </tr>
            
            <!-- Footer -->
            <tr>
              <td style="background-color:#f9fafb; padding:20px 32px; border-radius:0 0 8px 8px; border-top:1px solid #e5e7eb;">
                <p style="margin:0; font-size:12px; line-height:18px; color:#6b7280; text-align:center;">
                  For security, always verify payroll requests through the official Indigo Employee Portal.<br>
                  If you have concerns, contact Payroll directly.
                </p>
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
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7fa; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
      <tr>
        <td align="center" style="padding:40px 20px;">
          <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.08); max-width:600px;">
            <!-- Header -->
            <tr>
              <td style="background:linear-gradient(135deg, #ea580c 0%, #f97316 100%); padding:24px 32px; border-radius:8px 8px 0 0;">
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td>
                      <div style="color:#ffffff; font-size:20px; font-weight:600; letter-spacing:-0.5px;">Indigo Courier Service</div>
                      <div style="color:rgba(255,255,255,0.9); font-size:13px; margin-top:4px;">Package Delivery Notification</div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            
            <!-- Content -->
            <tr>
              <td style="padding:32px;">
                <p style="margin:0 0 16px 0; font-size:16px; line-height:24px; color:#1f2937;">Hi {recipient_name},</p>

                <p style="margin:0 0 20px 0; font-size:15px; line-height:24px; color:#374151;">
                  We attempted to deliver a package to your office address but were unable to complete the delivery.
      </p>

                <p style="margin:0 0 24px 0; font-size:15px; line-height:24px; color:#374151;">
                  Please confirm your delivery preferences so we can re-schedule the drop-off at your earliest convenience.
      </p>

                <div style="background-color:#fff7ed; border-left:4px solid #f97316; padding:16px; margin:24px 0; border-radius:4px;">
                  <p style="margin:0; font-size:14px; line-height:20px; color:#9a3412;">
                    <strong>Urgent:</strong> If no action is taken within 48 hours, your package may be returned to the sender.
                  </p>
                </div>
                
                <table width="100%" cellpadding="0" cellspacing="0" style="margin:28px 0;">
                  <tr>
                    <td align="center" style="padding:12px 0;">
                      <a href="{click_url}" style="background-color:#ea580c; color:#ffffff; text-decoration:none; padding:14px 32px; border-radius:6px; font-weight:600; font-size:15px; display:inline-block; box-shadow:0 2px 4px rgba(234,88,12,0.3);">
          Manage Delivery
        </a>
                    </td>
                  </tr>
                </table>
                
                <div style="border-top:1px solid #e5e7eb; margin-top:32px; padding-top:24px;">
                  <p style="margin:0 0 8px 0; font-size:14px; line-height:20px; color:#6b7280;">
                    Best regards,<br>
                    <strong style="color:#1f2937;">Indigo Courier Service</strong><br>
                    <a href="mailto:courier@indigo.co.uk" style="color:#ea580c; text-decoration:none;">courier@indigo.co.uk</a>
                  </p>
                </div>
              </td>
            </tr>
            
            <!-- Footer -->
            <tr>
              <td style="background-color:#f9fafb; padding:20px 32px; border-radius:0 0 8px 8px; border-top:1px solid #e5e7eb;">
                <p style="margin:0; font-size:12px; line-height:18px; color:#6b7280; text-align:center;">
                  Track your packages through the official Indigo Courier Service portal.<br>
                  For questions, contact our customer service team.
      </p>
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
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7fa; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
      <tr>
        <td align="center" style="padding:40px 20px;">
          <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.08); max-width:600px;">
            <!-- Header -->
            <tr>
              <td style="background:linear-gradient(135deg, #be185d 0%, #ec4899 100%); padding:24px 32px; border-radius:8px 8px 0 0;">
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td>
                      <div style="color:#ffffff; font-size:20px; font-weight:600; letter-spacing:-0.5px;">Indigo People &amp; Culture</div>
                      <div style="color:rgba(255,255,255,0.9); font-size:13px; margin-top:4px;">Human Resources Department</div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            
            <!-- Content -->
            <tr>
              <td style="padding:32px;">
                <p style="margin:0 0 16px 0; font-size:16px; line-height:24px; color:#1f2937;">Dear {recipient_name},</p>

                <p style="margin:0 0 20px 0; font-size:15px; line-height:24px; color:#374151;">
                  We have recently updated our <strong style="color:#1f2937;">Employee Code of Conduct and Remote Working Policy</strong>. 
        All staff are required to review and acknowledge the updated policy.
      </p>

                <div style="background-color:#fce7f3; border-left:4px solid #ec4899; padding:16px; margin:24px 0; border-radius:4px;">
                  <p style="margin:0; font-size:14px; line-height:20px; color:#9f1239;">
                    <strong>Mandatory Action:</strong> This acknowledgement is required and will form part of your employment record. 
                    Please complete this within 7 business days.
                  </p>
                </div>
                
                <table width="100%" cellpadding="0" cellspacing="0" style="margin:28px 0;">
                  <tr>
                    <td align="center" style="padding:12px 0;">
                      <a href="{click_url}" style="background-color:#be185d; color:#ffffff; text-decoration:none; padding:14px 32px; border-radius:6px; font-weight:600; font-size:15px; display:inline-block; box-shadow:0 2px 4px rgba(190,24,93,0.3);">
          Review Policy &amp; Acknowledge
        </a>
                    </td>
                  </tr>
                </table>
                
                <div style="border-top:1px solid #e5e7eb; margin-top:32px; padding-top:24px;">
                  <p style="margin:0 0 8px 0; font-size:14px; line-height:20px; color:#6b7280;">
                    Best regards,<br>
                    <strong style="color:#1f2937;">Indigo People &amp; Culture Team</strong><br>
                    <a href="mailto:hr@indigo.co.uk" style="color:#be185d; text-decoration:none;">hr@indigo.co.uk</a>
                  </p>
                </div>
              </td>
            </tr>
            
            <!-- Footer -->
            <tr>
              <td style="background-color:#f9fafb; padding:20px 32px; border-radius:0 0 8px 8px; border-top:1px solid #e5e7eb;">
                <p style="margin:0; font-size:12px; line-height:18px; color:#6b7280; text-align:center;">
                  Policy updates are communicated through official HR channels only.<br>
                  If you have questions, please contact the People &amp; Culture team directly.
      </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    """
    text = strip_tags(html)
    return text, html


SCENARIO_BUILDERS = {
    EmailTemplate.Scenario.IT_ALERT: build_it_security_alert_body,
    EmailTemplate.Scenario.PASSWORD_RESET: build_password_reset_body,
    EmailTemplate.Scenario.PAYROLL: build_payroll_body,
    EmailTemplate.Scenario.DELIVERY: build_delivery_failure_body,
    EmailTemplate.Scenario.HR_POLICY: build_hr_policy_body,
}


def send_campaign_emails(campaign: Campaign, request=None):
    """
    Send emails for a campaign to all linked recipients.
    Uses MailHog / configured SMTP backend in development.
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

        # Choose builder based on template scenario
        tpl = campaign.email_template
        builder = SCENARIO_BUILDERS.get(tpl.scenario, build_it_security_alert_body)

        text_main, html_main = builder(tpl, ctx, click_url, report_url)

        # Append a generic footer to text version
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
