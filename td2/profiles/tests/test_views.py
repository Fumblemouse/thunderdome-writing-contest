"""Test framework for users and profile views"""
from django.urls import reverse

# Create your tests here.
from baseapp.tests.test_utils import BaseAppTestCase


class TestProfileViewsAccess(BaseAppTestCase):
    """Test access to profile views"""

    def test_set_timezone_user_not_logged_in(self):
        """tests login required to set timezone"""
        response = self.client.get(reverse("set timezone"))
        self.assertRedirects(response, reverse("login"))

    def test_set_timezone_user_logged_in(self):
        """tests login sufficient for user to set timezone"""
        self.login_testuser(self.user)
        response = self.client.get(reverse("set timezone"))
        self.assertRedirects(response, reverse("home"))

    def test_signup_user_logged_in(self):
        """tests signup redirects if user logged in"""
        self.login_testuser("djangotestuser")
        response = self.client.get(reverse("sign up"))
        self.assertRedirects(response, reverse("profile"))

    def test_signup_user_not_logged_in(self):
        """Tests non-logged in user gets to signup"""
        response = self.client.get(reverse("sign up"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/sign-up.html")

    def test_settings_user_not_logged_in(self):
        """tests user required to log in to reach settings"""
        response = self.client.get(reverse("change settings"))
        self.assertRedirects(response, "/accounts/login/?next=/settings/")

    def test_settings_user_logged_in(self):
        """Tests user can reach settings when logge din"""
        self.login_testuser("djangotestuser")
        response = self.client.get(reverse("change settings"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/settings.html")

    def test_profile_user_logged_in(self):
        """tests user able to reach profile when logged in"""
        self.login_testuser(self.user)
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/profile.html")
