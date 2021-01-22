"""Test framework for users and profile views"""
from django.test import TestCase
from django.urls import reverse
# Create your tests here.
from django.contrib.auth import get_user_model
from profiles.models import Profile
from baseapp.tests.test_utils import login_testuser, set_up_story_private, set_up_story_public

class TestProfileViewsAccess(TestCase):
    def setUp(self):
        """set up user using usermodel"""
        #create the user and login
        User = get_user_model()
        self.user = User.objects.create_user(username='djangotestuser', password='12345abcde')
        self.user.profile.timezone = "Africa/Abidjan"
        self.user.save()

    def test_set_timezone_user_not_logged_in(self):
        response = self.client.get(reverse('set timezone'))
        self.assertRedirects(response, reverse('login'))

    def test_set_timezone_user_logged_in(self):
        login_testuser(self, self.user)
        response = self.client.get(reverse('set timezone'))
        self.assertRedirects(response, reverse('home'))

    def test_signup_user_logged_in(self):
        login_testuser(self, self.user)
        response = self.client.get(reverse('sign up'))
        self.assertRedirects(response, reverse('profile'))

    def test_signup_user_logged_in(self):
        response = self.client.get(reverse('sign up'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/sign-up.html')

    def test_settings_user_not_logged_in(self):
        response = self.client.get(reverse('change settings'))
        self.assertRedirects(response, '/accounts/login/?next=/settings/')

    def test_settings_user_logged_in(self):
        login_testuser(self, self.user)
        response = self.client.get(reverse('change settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/settings.html')

        def test_profile_user_logged_in(self):
        login_testuser(self, self.user)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile.html')



