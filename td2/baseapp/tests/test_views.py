"""Test framework for users and profiles"""
from django.test import TestCase
from django.urls import reverse

from baseapp.models import Story
# Create your tests here.
#things to check
#1. users can only get to create and edit stories if they are logged in
#2. users cannot view stories  if author has account as not viewable
#3. users cannot view stories  if author has story  as not viewable

"""class Story_Views_Test(SetUp_Class):

    def setUp(self):
        set up user using usermodel
        #create the user and login
        user = get_user_model()
        self.user = user.objects.create_user(username='djangotestuser1', password='12345')
        Story.objects.create(title = "test story 1", author = self.user, content = "test story 1 content")

    def test_edit_story_view_no_login(self):
        response = self.client.get.reverse("/")
        self.assertEqual(response.status_code, 302)

    def test_home_view_no_login(self):
        user_login = self.client.login(email="user@mp.com", password="user")
        self.assertTrue(user_login)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)        

    def test_add_user_view(self):
        response = self.client.get("include url for add user view")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "include template name to render the response")

    # Invalid Data
    def test_add_user_invalidform_view(self):
        response = self.client.post("include url to post the data given", {'email': "admin@mp.com", 'password': "", 'first_name': "mp", 'phone': 12345678})
        self.assertTrue('"error": true' in response.content)

    # Valid Data
    def test_add_admin_form_view(self):
        user_count = User.objects.count()
        response = self.client.post("include url to post the data given", {'email': "user@mp.com", 'password': "user", 'first_name': "user"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), user_count+1)
        self.assertTrue('"error": false' in response.content)
        """