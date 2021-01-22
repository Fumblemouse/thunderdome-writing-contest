"""Test framework for users and profiles"""
from django.test import TestCase
# Create your tests here.
from django.contrib.auth import get_user_model
from baseapp.forms import StoryForm

class Story_Form_Test(TestCase):
    """Test user of story form"""
    def setUp(self):
        """set up user using usermodel"""
        #create the user and login
        user = get_user_model()
        self.user = user.objects.create_user(username='djangotestuser1', password='12345')

    def test_storyform_valid(self):
        """test form is valid"""
        form = StoryForm(data={"title": "Test Story 1", "content":"This the body of Test story 1"})

        self.assertTrue(
            form.is_valid()
        )

    def test_storyform_invalid(self):
        """test its invalid with no content"""
        form = StoryForm(data={"title": "Test Story 1", "content":""})

        self.assertFalse(
            form.is_valid()
        )
    def test_base_form_characteristics(self):
        """test base form child is inheriting characteristics"""
        form = StoryForm(data={"title": "Test Story 1", "content":"This the body of Test story 1", "public_view_allowed":False})
        for fieldname,field in form.fields.items():
            if "Boolean" not in str(field):
                self.assertTrue('form-control' in field.widget.attrs['class'])
            else:
                self.assertTrue('form-check-input' in field.widget.attrs['class'])
