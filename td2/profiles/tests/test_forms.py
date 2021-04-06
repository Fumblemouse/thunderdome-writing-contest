"""Test framework for users and profile forms"""
from django.test import TestCase
# Create your tests here.
from profiles.forms import SignUpForm, UserUpdateForm
from profiles.models import CustomUser

class SignUpFormTest(TestCase):
    """Signup form test"""
    def test_sign_up_help_text(self):
        form = SignUpForm()
        self.assertEqual(form.fields['first_name'].help_text, 'Optional')
        self.assertEqual(form.fields['first_name'].max_length, 100)
        self.assertEqual(form.fields['last_name'].help_text, 'Also optional')
        self.assertEqual(form.fields['last_name'].max_length, 100)
        self.assertEqual(form.fields['email'].help_text, 'Used only you send you notifications of things you have chosen to do')
        self.assertEqual(form.fields['email'].max_length, 150)
    def test_sign_up_form_valid(self):
        form = SignUpForm(data={"username": "djangotestuser1", "email":"this@email.com", "password1":"ai876986akjhdf", "password2":"ai876986akjhdf" })
        self.assertTrue(form.is_valid())
    def test_sign_up_form_email_valid(self):
        form = SignUpForm(data={"username": "djangotestuser1", "email":"email.com", "password1":"a2876986akjhdf", "password2":"a2876986akjhdf" })
        self.assertTrue(form.errors)
    def test_sign_up_form_password_synch_valid(self):
        form = SignUpForm(data={"username": "djangotestuser1", "email":"fred@email.com", "password1":"ai876986akjhdf", "password2":"a2876986akjhdf" })
        self.assertTrue(form.errors)

class UserUpdateFormTest(TestCase):
    """user update form test"""
    def setUp(self):
        self.form = UserUpdateForm(data={
            "email": "fish@chips.com",
            "first_name": "Theodore",
            "last_name": "Roosevelt",
            "bio": "born",
            "highest_access": CustomUser.PRIVATE})
    def test_user_update_form_valid(self):
        self.assertTrue(self.form.is_valid())

class UserLoginFormTest(TestCase):
    """We are only testing the classes here because Django requires a legit login to validate against, which is a security risk"""
    def setUp(self):
        self.form = UserUpdateForm(data={"username": "Tim", "password": "12345abcde"})
    def test_user_login_field_class(self):
        for fieldname,field in self.form.fields.items():
            if "Boolean" not in str(field):
                self.assertTrue('form-control' in field.widget.attrs['class'])
            else:
                self.assertTrue('form-check-input' in field.widget.attrs['class'])

