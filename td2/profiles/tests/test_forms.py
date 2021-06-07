"""Test framework for users and profile forms"""
from django.test import TestCase
from django.contrib.auth import get_user_model
# Create your tests here.
from profiles.forms import SignUpForm, UserUpdateForm, UserPasswordChangeForm
from profiles.models import CustomUser


class SignUpFormTest(TestCase):
    """Signup form test"""
    def test_sign_up_help_text(self):
        """Test help text i spresesent in signup form"""
        form = SignUpForm()
        self.assertEqual(form.fields['first_name'].help_text, 'Optional')
        self.assertEqual(form.fields['first_name'].max_length, 100)
        self.assertEqual(form.fields['last_name'].help_text, 'Also optional')
        self.assertEqual(form.fields['last_name'].max_length, 100)
        self.assertEqual(form.fields['email'].help_text, 'Used only you send you notifications of things you have chosen to do')
        self.assertEqual(form.fields['email'].max_length, 150)
    def test_sign_up_form_valid(self):
        """Test sign up form is valid"""
        form = SignUpForm(data={"username": "djangotestuser1", "email":"this@email.com", "password1":"ai876986akjhdf", "password2":"ai876986akjhdf" })
        self.assertTrue(form.is_valid())
    def test_sign_up_form_email_valid(self):
        """Test sign up email is valid"""
        form = SignUpForm(data={"username": "djangotestuser1", "email":"email.com", "password1":"a2876986akjhdf", "password2":"a2876986akjhdf" })
        self.assertTrue(form.errors)
    def test_sign_up_form_password_synch_valid(self):
        """Test sign up password form is valid"""
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
            "highest_access": CustomUser.PRIVATE,
            "private_profile": False,
            })
    def test_user_update_form_valid(self):
        """Test user update form is valid"""
        self.assertTrue(self.form.is_valid())

class UserLoginFormTest(TestCase):
    """We are only testing the classes here because Django requires a legit login to validate against, which is a security risk"""
    def setUp(self):
        self.form = UserUpdateForm()
    def test_user_login_field_class(self):
        """Test classes are added to form types for bootstrap"""
        for fieldname, field in self.form.fields.items():
            if "Boolean" not in str(field):
                self.assertTrue('form-control' in field.widget.attrs['class'])
            else:
                self.assertTrue('form-check-input' in field.widget.attrs['class'])

class UserChangePasswordFormTest(TestCase):
    """Test User Passord Change Form"""
    @classmethod
    def setUpTestData(cls):
        """Set up password change form"""
        cls.User = get_user_model()
        cls.user = cls.User.objects.create_user(username='djangotestuser', password='12345abcde')
        cls.form = UserPasswordChangeForm(cls.user, data={
            "old_password": "12345abcde",
            "new_password1": "Theodore",
            "new_password2": "Theodore",
            })
    def test_user_change_password_is_valid(self):
        """Test password change form is valid"""
        self.assertTrue(self.form.is_valid())
