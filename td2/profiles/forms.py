"""Forms for profile app"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from baseapp.forms import BaseForm
from .models import Profile

class BaseUserCreationForm(UserCreationForm):
    """BaseForm to bootstrapping"""
    def __init__(self, *args, **kwargs):
        super(BaseUserCreationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if "Boolean" not in str(field):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'

class SignUpForm(BaseUserCreationForm):
    """Sign up form"""
    first_name = forms.CharField(max_length=100, help_text='Optional', required=False)
    last_name = forms.CharField(max_length=100, help_text='Also optional', required=False)
    email = forms.EmailField(max_length=150, help_text='Used only you send you notifications of things you have chosen to do')

    class Meta:
        model = get_user_model()
        fields = 'username', 'email', 'first_name', 'last_name', 'password1', 'password2'

class UserUpdateForm(BaseForm):
    """Update user fields"""
    class Meta:
        model=get_user_model()
        fields=['email', 'first_name', 'last_name']


class ProfileUpdateForm(BaseForm):
    """update profile model fields"""

    class Meta:
        model = Profile
        fields = 'bio', 'public_profile'
