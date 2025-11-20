from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTests(TestCase):
    def test_user_roles(self):
        u = User.objects.create_user(username="test", password="pass")
        self.assertEqual(u.role, "VIEWER")


class AuthTests(TestCase):
    def test_login_page_loads(self):
        res = self.client.get(reverse("login"))
        self.assertEqual(res.status_code, 200)


class RoleRequiredTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin1", password="pass", role="ADMIN"
        )
        self.instructor = User.objects.create_user(
            username="instructor1", password="pass", role="INSTRUCTOR"
        )
        self.viewer = User.objects.create_user(
            username="viewer1", password="pass", role="VIEWER"
        )

    def test_instructor_dashboard_allows_admin(self):
        self.client.login(username="admin1", password="pass")
        res = self.client.get("/instructor/")
        self.assertEqual(res.status_code, 200)

    def test_instructor_dashboard_allows_instructor(self):
        self.client.login(username="instructor1", password="pass")
        res = self.client.get("/instructor/")
        self.assertEqual(res.status_code, 200)

    def test_instructor_dashboard_blocks_viewer(self):
        self.client.login(username="viewer1", password="pass")
        res = self.client.get("/instructor/")
        self.assertEqual(res.status_code, 403)

