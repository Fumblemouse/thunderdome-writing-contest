"""Describe custom forms"""
from baseapp.forms import BaseForm
from universal.models import MiniDome

class MiniDomePublicForm(BaseForm):
    """USer enters Story and Title"""

    class Meta:
        model = MiniDome
        fields = ('winner')

class MiniDomeLoggedInForm(BaseForm):
    """USer enters Story and Title"""

    class Meta:
        model = MiniDome
        fields = ('winner', 'content')