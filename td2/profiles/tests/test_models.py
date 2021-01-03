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
        user = get_user_model()
        self.user = user.objects.create_user(username='djangotestuser', password='12345')
        
        #creating user creates profile because of save signals
    
    def test_profile(self):
        """test that signal works to create associated profile"""
        user = get_user_model()                                                                                    
        profile = user.objects.get(username = self.user.username).profile