"""Test framework for users and profiles"""
from django.test import TestCase
from django.urls import reverse
# Create your tests here.
from django.contrib.auth import get_user_model
from profiles.models import Profile

class TestProfileView(TestCase):
    def setUp(self):
        """set up user using usermodel"""
        #create the user and login
        user = get_user_model()
        self.user = user.objects.create_user(username='djangotestuser', password='12345')
          
    def test_settings_form(self):
        #Use the view to create a profile
        self.client.login(username='djangotestuser', password='12345')
        #get the newly created profile and add to it via the form
        profile = Profile.objects.get(pk = self.user)
        response = self.client.post(
            reverse('change settings'),
            {'bio': 'born', 'public_profile': False, 'timezone': 'Pacific/Auckland'}
        )
        self.assertEqual(response.status_code, 302)
        profile.refresh_from_db()
        self.assertEqual(profile.bio, 'born')
        self.assertEqual(profile.public_profile, False)
        self.assertEqual(profile.timezone, 'Pacific/Auckland')
