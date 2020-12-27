"""Forms for profile app"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Profile

class SignUpForm(UserCreationForm):
    """Sign up form"""
    first_name = forms.CharField(max_length=100, help_text='Optional', required=False)
    last_name = forms.CharField(max_length=100, help_text='Also optional', required=False)
    email = forms.EmailField(max_length=150, help_text='Used only you send you notifications of things you have chosen to do')

    class Meta:
        model = get_user_model()
        fields = 'username', 'email', 'first_name', 'last_name', 'password1', 'password2'

class UserUpdateForm(forms.ModelForm):
    """Update user fields"""
    class Meta:
        model=get_user_model()
        fields=['email', 'first_name', 'last_name']


class ProfileUpdateForm(forms.ModelForm):
    """update profile model fields"""
    model = Profile
    bio = forms.CharField(widget=forms.Textarea,required=False)
    public_profile = forms.BooleanField(required=False)
    class Meta:
        model = get_user_model()
        fields = 'bio', 'public_profile'
