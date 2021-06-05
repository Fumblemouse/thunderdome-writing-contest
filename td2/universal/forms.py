"""Describe custom forms"""
from django.db.models import Q

from baseapp.forms import BaseForm

from baseapp.models import Story
from .models import MiniDome

class MiniDomePublicForm(BaseForm):
    """USer enters Story and Title"""

    class Meta:
        model = MiniDome
        fields = ('winner',)

    def __init__(self, stories, *args, **kwargs):
        super(MiniDomePublicForm, self).__init__(*args, **kwargs)
        #check to make sure form hasn't been posted
        self.stories = stories
        if not self.is_bound:
            self.fields['winner'].queryset = Story.objects.filter(Q(pk=self.stories[0]) | Q(pk=self.stories[1]))

class MiniDomeLoggedInForm(BaseForm):
    """USer enters Story and Title"""

    class Meta:
        model = MiniDome
        fields = ('winner', 'content')

    def __init__(self, stories, *args, **kwargs):
        super(MiniDomeLoggedInForm, self).__init__(*args, **kwargs)
        #check to make sure form hasn't been posted
        self.stories = stories
        if not self.is_bound:
            self.fields['winner'].queryset = Story.objects.filter(Q(pk=self.stories[0]) | Q(pk=self.stories[1]))