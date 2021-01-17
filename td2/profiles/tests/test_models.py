"""Test models for users and profiles"""
from django.test import TestCase
# Create your tests here.
from django.contrib.auth import get_user_model
from profiles.models import Profile

class ProfileCreationTest(TestCase):
    """test for users and profile"""
    def setUp(self):
        """set up user using usermodel"""
        #create the user and login
        #creating user creates profile because of save signals
        self.usermodel = get_user_model()
        self.user = self.usermodel.objects.create_user(username='DjangoTestUser', password='12345')
        self.profile = self.usermodel.objects.get(username = self.user.username).profile 
    def test_profile(self):
        """test that signal works to create associated profile"""
        self.assertTrue(self.profile)
    def test_profile_string_representation(self):
        """test object name function works"""
        self.profile = self.usermodel.objects.get(username = self.user.username).profile
        self.assertEqual(str(self.profile), self.user.username)
    def test_profile_slug(self):
        """test profile slug is created on save"""
        self.profile.save()
        self.assertEqual(self.profile.slug, "djangotestuser")
