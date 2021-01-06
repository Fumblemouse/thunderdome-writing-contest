"""Describes custom forms"""
from django.utils import timezone
from django import forms
from django.utils.translation import gettext_lazy as _
from baseapp.forms import BaseForm


#from flatpickr import DateTimePickerInput

from .models import Prompt, Contest, Entry, Crit

class PromptForm(BaseForm):
    """User creates Prompt details"""
    class Meta:
        model = Prompt
        fields = ('title', 'content',)

class CreateContestNewPromptForm(BaseForm):
    """User creates Prompt details"""

    class Meta:
        model = Contest
        fields = ('wordcount', 'start_date','expiry_date' )
"""        widgets = {
            'start_date': DateTimePickerInput(),
            'expiry_date': DateTimePickerInput(),
        }"""

class CreateContestOldPromptForm(BaseForm):
    """User creates Prompt details"""

    class Meta:
        model = Contest
        fields = ('prompt','wordcount','start_date','expiry_date' )
        """widgets = {
            'start_date': DateTimePickerInput(),
            'expiry_date': DateTimePickerInput(),
        }"""

class EnterContestNewStoryForm(BaseForm):
    """User creates New Story to enter contest"""
    class Meta:
        model = Entry
        fields = ()

    def __init__(self, *args, **kwargs):
        self.story_wordcount = kwargs.pop('story_wordcount')
        self.contest_wordcount = kwargs.pop('contest_wordcount')
        self.expiry_date = kwargs.pop('contest_expiry_date')
        super(EnterContestNewStoryForm, self).__init__(*args, **kwargs)

    def clean(self):
      # check if wordcount is excessive

        if self.story_wordcount > self.contest_wordcount:
            raise forms.ValidationError("More words than wordcount. Kill your darlings!")
        if self.expiry_date < timezone.now():
            raise forms.ValidationError("The deadline for that contest is over.")
        return self.cleaned_data  # never forget this! ;o)

class EnterCritForm(BaseForm):
    """user enters comments and score for story"""
    class Meta:
        model = Crit
        fields = ('content', 'score', 'final')
        labels = {
            'content': _('Critique'),
        }
