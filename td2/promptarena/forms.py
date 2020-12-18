"""Describes custom forms"""
from django import forms
from .models import Prompt

class CreatePrompt(forms.ModelForm):
    """User creates Prompt details"""
    class Meta:
        model = Prompt
        fields = ('title', 'content',)
