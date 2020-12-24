"""Describes custom forms"""
from django import forms
from .models import Story

class CreateStoryForm(forms.ModelForm):
    """USer enters Story and Title"""

    class Meta:
        model = Story
        fields = ('title', 'content','public_view_allowed')
"""
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'allow_public_display')
"""