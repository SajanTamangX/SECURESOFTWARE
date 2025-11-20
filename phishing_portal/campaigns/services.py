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
    <div style="font-family: Arial, sans-serif; background:#ffffff; padding:20px;
                border-radius:8px; border:1px solid #e3e3e3; color:#333; max-width:620px; margin:auto">

      <div style="padding-bottom:16px; border-bottom:1px solid #ddd;">
          <span style="font-size:20px; font-weight:600; color:#0B57D0;">
              Indigo IT Security
          </span>
      </div>

      <p style="font-size:15px; margin-top:20px;">Hi {recipient_name},</p>

      <p>
        We detected a new sign-in to your <strong>Indigo Employee Portal</strong> account
        from a device or location we don't recognise.
      </p>

      <p style="margin-top:18px;">
        If this was you, no further action is required. If this wasn't you, please review your
        recent activity immediately.
      </p>

      <p style="margin-top:22px;">
        <a href="{click_url}"
           style="background:#0B57D0; color:#fff; padding:11px 18px; text-decoration:none;
                  border-radius:4px; font-weight:600; display:inline-block;">
          Review Account Activity
        </a>
      </p>

      <p style="margin-top:10px;">
        <a href="{report_url}"
           style="background:#d9534f; color:#fff; padding:10px 18px; text-decoration:none;
                  border-radius:4px; font-weight:600; display:inline-block;">
          Report this Email
        </a>
      </p>

      <p style="margin-top:26px;">
        Kind regards,<br>
        <strong>Indigo IT Security Team</strong><br>
        security@indigo.co.uk
      </p>

    </div>
    """
    text = strip_tags(html)
    return text, html


def build_password_reset_body(email_template, ctx, click_url, report_url):
    recipient_name = _safe_name(ctx)
    html = f"""
    <div style="font-family: Arial, sans-serif; background:#ffffff; padding:22px;
                border-radius:8px; border:1px solid #e1e1e1; color:#333; max-width:620px; margin:auto">

      <div style="padding-bottom:14px; border-bottom:1px solid #ddd;">
        <span style="font-size:19px; font-weight:600; color:#0B57D0;">
          Indigo Accounts
        </span>
      </div>

      <p style="font-size:15px; margin-top:20px;">Hello {recipient_name},</p>

      <p>
        A request was received to reset the password for your
        <strong>Indigo Single Sign-On</strong> account.
      </p>

      <p style="margin-top:16px;">
        If you made this request, please confirm it by clicking the button below.
      </p>

      <p style="margin:22px 0 10px 0;">
        <a href="{click_url}"
           style="background:#0B57D0; color:#fff; padding:11px 24px; text-decoration:none;
                  border-radius:4px; font-weight:600; display:inline-block;">
          Confirm Password Reset
        </a>
      </p>

      <p style="margin-top:0;">
        <a href="{report_url}"
           style="background:#d9534f; color:#fff; padding:10px 18px; text-decoration:none;
                  border-radius:4px; font-weight:600; display:inline-block;">
          Report this Email
        </a>
      </p>

      <p style="font-size:13px; color:#555; margin-top:24px;">
        If you did <strong>not</strong> make this request, please contact IT Support immediately.
      </p>

    </div>
    """
    text = strip_tags(html)
    return text, html


def build_payroll_body(email_template, ctx, click_url, report_url):
    recipient_name = _safe_name(ctx)
    html = f"""
    <div style="font-family: Arial, sans-serif; background:#ffffff; padding:22px;
                border-radius:8px; border:1px solid #e1e1e1; color:#333; max-width:620px; margin:auto">

      <div style="padding-bottom:14px; border-bottom:1px solid #ddd;">
        <span style="font-size:19px; font-weight:600; color:#0B57D0;">
          Indigo Payroll
        </span>
      </div>

      <p style="font-size:15px; margin-top:20px;">Dear {recipient_name},</p>

      <p>
        As part of our end-of-month payroll checks, we were unable to automatically verify
        your current bank details.
      </p>

      <p>
        To avoid any delay to your salary payment, please review and confirm your details
        in the Employee Payroll Portal.
      </p>

      <p style="margin:22px 0 10px 0;">
        <a href="{click_url}"
           style="background:#0B57D0; color:#fff; padding:11px 24px; text-decoration:none;
                  border-radius:4px; font-weight:600; display:inline-block;">
          Review Payroll Details
        </a>
      </p>

      <p style="margin-top:0;">
        <a href="{report_url}"
           style="background:#d9534f; color:#fff; padding:10px 18px; text-decoration:none;
                  border-radius:4px; font-weight:600; display:inline-block;">
          Report this Email
        </a>
      </p>

      <p style="font-size:13px; color:#555; margin-top:24px;">
        This verification should take less than two minutes to complete.
      </p>

    </div>
    """
    text = strip_tags(html)
    return text, html


def build_delivery_failure_body(email_template, ctx, click_url, report_url):
    recipient_name = _safe_name(ctx)
    html = f"""
    <div style="font-family: Arial, sans-serif; background:#ffffff; padding:22px;
                border-radius:8px; border:1px solid #e1e1e1; color:#333; max-width:620px; margin:auto">

      <div style="padding-bottom:14px; border-bottom:1px solid #ddd;">
        <span style="font-size:19px; font-weight:600; color:#0B57D0;">
          Indigo Courier Service
        </span>
      </div>

      <p style="font-size:15px; margin-top:20px;">Hi {recipient_name},</p>

      <p>
        We attempted to deliver a package to your office address but were unable to complete
        the delivery.
      </p>

      <p style="margin-top:16px;">
        Please confirm your delivery preferences so we can re-schedule the drop-off.
      </p>

      <p style="margin:22px 0 10px 0;">
        <a href="{click_url}"
           style="background:#0B57D0; color:#fff; padding:10px 22px; text-decoration:none;
                  border-radius:4px; font-weight:600; display:inline-block;">
          Manage Delivery
        </a>
      </p>

      <p style="margin-top:0;">
        <a href="{report_url}"
           style="background:#d9534f; color:#fff; padding:10px 18px; text-decoration:none;
                  border-radius:4px; font-weight:600; display:inline-block;">
          Report this Email
        </a>
      </p>

      <p style="font-size:13px; color:#555; margin-top:24px;">
        If no action is taken within 48 hours, your package may be returned to the sender.
      </p>

    </div>
    """
    text = strip_tags(html)
    return text, html


def build_hr_policy_body(email_template, ctx, click_url, report_url):
    recipient_name = _safe_name(ctx)
    html = f"""
    <div style="font-family: Arial, sans-serif; background:#ffffff; padding:22px;
                border-radius:8px; border:1px solid #e1e1e1; color:#333; max-width:620px; margin:auto">

      <div style="padding-bottom:14px; border-bottom:1px solid #ddd;">
        <span style="font-size:19px; font-weight:600; color:#0B57D0;">
          Indigo People &amp; Culture
        </span>
      </div>

      <p style="font-size:15px; margin-top:20px;">Dear {recipient_name},</p>

      <p>
        We have recently updated our <strong>Employee Code of Conduct and Remote Working Policy</strong>.
        All staff are required to review and acknowledge the updated policy.
      </p>

      <p style="margin:22px 0 10px 0;">
        <a href="{click_url}"
           style="background:#0B57D0; color:#fff; padding:11px 24px; text-decoration:none;
                  border-radius:4px; font-weight:600; display:inline-block;">
          Review Policy &amp; Acknowledge
        </a>
      </p>

      <p style="margin-top:0;">
        <a href="{report_url}"
           style="background:#d9534f; color:#fff; padding:10px 18px; text-decoration:none;
                  border-radius:4px; font-weight:600; display:inline-block;">
          Report this Email
        </a>
      </p>

      <p style="font-size:13px; color:#555; margin-top:24px;">
        This acknowledgement is mandatory and forms part of your employment record.
      </p>

    </div>
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
        <html>
          <body style="font-family:Arial,sans-serif;background:#ffffff;">
            {html_main}
            <img src="{open_url}" width="1" height="1"
                 style="display:none;" alt="" />
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
