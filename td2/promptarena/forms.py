"""Describes custom forms"""
from django import forms
from tinymce.widgets import TinyMCE
from .models import Prompt

class EnterPrompt(forms.ModelForm):
    """USer enters Prompt details"""
    #content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    class Meta:
        model = Prompt
        fields = ('title', 'content',)
        