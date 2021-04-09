"""Forms for profile app"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from baseapp.forms import BaseForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """BaseForm to bootstrapping"""
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if "Boolean" not in str(field):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'
    class Meta:
        model = CustomUser
        fields = 'username', 'password'

class SignUpForm(CustomUserCreationForm):
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
        fields= ('email', 'first_name', 'last_name', 'bio', 'private_profile', 'highest_access')

"""
class ProfileUpdateForm(BaseForm):
    update profile model fields

    class Meta:
        model = Profile
        fields = 'bio', 'public_profile'
"""

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '', 'id': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': '',
            'id': 'password',
        }
    ))

class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)

    #class Meta:
    old_password = forms.CharField(
        widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': '',
            'id': 'old_password',
        }
    ))
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': '',
                'id': 'new_password1',
            },
        )
    )
    new_password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': '',
                'id': 'new_password2',
            },
        )
    )

