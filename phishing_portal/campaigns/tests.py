from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core import mail
from .models import EmailTemplate, Campaign, CampaignRecipient, Recipient, Event, AuditLog

User = get_user_model()


class CampaignModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="inst1", password="pass", role="INSTRUCTOR"
        )
        self.template = EmailTemplate.objects.create(
            name="Test Template",
            subject="Hello",
            body="Hi {{ first_name }}",
            created_by=self.user,
        )

    def test_create_campaign(self):
        campaign = Campaign.objects.create(
            name="Test Campaign",
            description="Demo",
            email_template=self.template,
            created_by=self.user,
            scheduled_for=timezone.now(),
        )
        self.assertEqual(campaign.email_template, self.template)


class CampaignPermissionTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username="inst", password="pass", role="INSTRUCTOR"
        )
        self.viewer = User.objects.create_user(
            username="view", password="pass", role="VIEWER"
        )

    def test_instructor_can_access_new_campaign(self):
        self.client.login(username="inst", password="pass")
        resp = self.client.get(reverse("campaigns:campaign_create"))
        self.assertEqual(resp.status_code, 200)

    def test_viewer_cannot_access_new_campaign(self):
        self.client.login(username="view", password="pass")
        resp = self.client.get(reverse("campaigns:campaign_create"))
        self.assertEqual(resp.status_code, 403)


class TrackingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="inst2", password="pass", role="INSTRUCTOR"
        )
        self.template = EmailTemplate.objects.create(
            name="Track Template",
            subject="Track Me",
            body="Hello {{ first_name }}",
            created_by=self.user,
        )
        self.campaign = Campaign.objects.create(
            name="Track Campaign",
            description="Testing tracking.",
            email_template=self.template,
            created_by=self.user,
            scheduled_for=timezone.now(),
        )
        self.recipient = Recipient.objects.create(
            email="alice@example.com",
            first_name="Alice",
        )
        self.cr = CampaignRecipient.objects.create(
            campaign=self.campaign,
            recipient=self.recipient,
        )

    def test_send_campaign_creates_email_with_tracking_links(self):
        self.client.login(username="inst2", password="pass")
        url = reverse("campaigns:send_campaign", kwargs={"pk": self.campaign.pk})
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        tracking_id = str(self.cr.tracking_id)
        self.assertIn(tracking_id, body)

    def test_open_click_report_create_events(self):
        tracking_id = str(self.cr.tracking_id)
        open_url = reverse("campaigns:track_open", kwargs={"tracking_id": tracking_id})
        click_url = reverse("campaigns:track_click", kwargs={"tracking_id": tracking_id})
        report_url = reverse("campaigns:track_report", kwargs={"tracking_id": tracking_id})
        
        self.client.get(open_url)
        self.client.get(click_url)
        self.client.get(report_url)
        
        types = list(Event.objects.values_list("event_type", flat=True))
        self.assertIn(Event.Type.OPEN, types)
        self.assertIn(Event.Type.CLICK, types)
        self.assertIn(Event.Type.REPORT, types)


class AuditLogTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="pass", role="ADMIN"
        )
        self.instructor = User.objects.create_user(
            username="inst", password="pass", role="INSTRUCTOR"
        )
        self.viewer = User.objects.create_user(
            username="view", password="pass", role="VIEWER"
        )
        self.template = EmailTemplate.objects.create(
            name="Test Template",
            subject="Hello",
            body="Hi {{ first_name }}",
            created_by=self.admin,
        )

    def test_template_creation_logs_action(self):
        """Test that creating a template creates an audit log entry."""
        self.client.login(username="admin", password="pass")
        initial_count = AuditLog.objects.count()
        
        url = reverse("campaigns:template_create")
        resp = self.client.post(url, {
            "name": "New Template",
            "subject": "Test Subject",
            "body": "Test Body",
        })
        
        self.assertEqual(resp.status_code, 302)  # Redirect after success
        self.assertEqual(AuditLog.objects.count(), initial_count + 1)
        
        log = AuditLog.objects.latest("created_at")
        self.assertEqual(log.user, self.admin)
        self.assertEqual(log.action, "Created email template")
        self.assertIn("New Template", log.details)
        self.assertIn("ID:", log.details)

    def test_campaign_creation_logs_action(self):
        """Test that creating a campaign creates an audit log entry."""
        self.client.login(username="admin", password="pass")
        initial_count = AuditLog.objects.count()
        
        url = reverse("campaigns:campaign_create")
        scheduled_time = timezone.now()
        resp = self.client.post(url, {
            "name": "New Campaign",
            "description": "Test Description",
            "email_template": self.template.id,
            "scheduled_for": scheduled_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "DRAFT",
        })
        
        self.assertEqual(resp.status_code, 302)  # Redirect after success
        self.assertEqual(AuditLog.objects.count(), initial_count + 1)
        
        log = AuditLog.objects.latest("created_at")
        self.assertEqual(log.user, self.admin)
        self.assertEqual(log.action, "Created campaign")
        self.assertIn("New Campaign", log.details)
        self.assertIn("ID:", log.details)

    def test_upload_recipients_logs_action(self):
        """Test that uploading recipients creates an audit log entry."""
        self.client.login(username="admin", password="pass")
        campaign = Campaign.objects.create(
            name="Test Campaign",
            description="Test",
            email_template=self.template,
            created_by=self.admin,
            scheduled_for=timezone.now(),
        )
        initial_count = AuditLog.objects.count()
        
        import io
        import csv
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        csv_data = io.StringIO()
        writer = csv.writer(csv_data)
        writer.writerow(["email", "first_name", "last_name"])
        writer.writerow(["test@example.com", "Test", "User"])
        csv_content = csv_data.getvalue().encode("utf-8")
        csv_file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")
        
        url = reverse("campaigns:upload_recipients", kwargs={"pk": campaign.pk})
        resp = self.client.post(url, {
            "csv_file": csv_file,
        })
        
        self.assertEqual(resp.status_code, 302)  # Redirect after success
        self.assertEqual(AuditLog.objects.count(), initial_count + 1)
        
        log = AuditLog.objects.latest("created_at")
        self.assertEqual(log.user, self.admin)
        self.assertEqual(log.action, "Uploaded recipients")
        self.assertIn("Test Campaign", log.details)
        self.assertIn("ID:", log.details)

    def test_send_campaign_logs_action(self):
        """Test that sending a campaign creates an audit log entry."""
        self.client.login(username="admin", password="pass")
        campaign = Campaign.objects.create(
            name="Test Campaign",
            description="Test",
            email_template=self.template,
            created_by=self.admin,
            scheduled_for=timezone.now(),
        )
        recipient = Recipient.objects.create(email="test@example.com")
        CampaignRecipient.objects.create(campaign=campaign, recipient=recipient)
        
        initial_count = AuditLog.objects.count()
        
        url = reverse("campaigns:send_campaign", kwargs={"pk": campaign.pk})
        resp = self.client.post(url)
        
        self.assertEqual(resp.status_code, 302)  # Redirect after success
        self.assertEqual(AuditLog.objects.count(), initial_count + 1)
        
        log = AuditLog.objects.latest("created_at")
        self.assertEqual(log.user, self.admin)
        self.assertEqual(log.action, "Sent campaign emails")
        self.assertIn("Test Campaign", log.details)
        self.assertIn("ID:", log.details)

    def test_audit_log_has_ip_and_user_agent(self):
        """Test that audit logs capture IP address and user agent."""
        self.client.login(username="admin", password="pass")
        initial_count = AuditLog.objects.count()
        
        url = reverse("campaigns:template_create")
        resp = self.client.post(
            url,
            {
                "name": "Test Template IP",
                "subject": "Test Subject",
                "body": "Test Body",
            },
            HTTP_USER_AGENT="Test User Agent",
        )
        
        self.assertEqual(resp.status_code, 302)  # Redirect after success
        self.assertEqual(AuditLog.objects.count(), initial_count + 1)
        
        log = AuditLog.objects.latest("created_at")
        self.assertTrue(log.ip_address)  # Should be hashed IP
        self.assertTrue(len(log.ip_address) == 64)  # SHA-256 hex length
        self.assertEqual(log.user_agent, "Test User Agent")  # Should have user agent

    def test_admin_can_access_audit_logs(self):
        """Test that admin users can access the audit logs page."""
        self.client.login(username="admin", password="pass")
        url = reverse("audit_logs")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Audit Logs", resp.content.decode())

    def test_instructor_cannot_access_audit_logs(self):
        """Test that instructor users cannot access the audit logs page."""
        self.client.login(username="inst", password="pass")
        url = reverse("audit_logs")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_viewer_cannot_access_audit_logs(self):
        """Test that viewer users cannot access the audit logs page."""
        self.client.login(username="view", password="pass")
        url = reverse("audit_logs")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_anonymous_cannot_access_audit_logs(self):
        """Test that anonymous users are redirected to login."""
        url = reverse("audit_logs")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)  # Redirect to login
        self.assertIn("/login/", resp.url)


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="pass", role="ADMIN"
        )
        self.instructor = User.objects.create_user(
            username="inst", password="pass", role="INSTRUCTOR"
        )
        self.viewer = User.objects.create_user(
            username="view", password="pass", role="VIEWER"
        )

    def test_admin_can_access_dashboard(self):
        """Test that admin users can access the dashboard."""
        self.client.login(username="admin", password="pass")
        url = reverse("dashboard")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Analytics Dashboard", resp.content.decode())

    def test_instructor_can_access_dashboard(self):
        """Test that instructor users can access the dashboard."""
        self.client.login(username="inst", password="pass")
        url = reverse("dashboard")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Analytics Dashboard", resp.content.decode())

    def test_viewer_cannot_access_dashboard(self):
        """Test that viewer users cannot access the dashboard."""
        self.client.login(username="view", password="pass")
        url = reverse("dashboard")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)
