"""Describes custom forms"""
from django import forms
from django.core.exceptions import ValidationError
#from flatpickr import DateTimePickerInput
from .models import Prompt, Contest, Entry

class CreatePromptForm(forms.ModelForm):
    """User creates Prompt details"""
    class Meta:
        model = Prompt
        fields = ('title', 'content',)

class CreateContestNewPromptForm(forms.ModelForm):
    """User creates Prompt details"""

    class Meta:
        model = Contest
        fields = ('wordcount', 'start_date','expiry_date' )
"""        widgets = {
            'start_date': DateTimePickerInput(),
            'expiry_date': DateTimePickerInput(),
        }"""

class CreateContestOldPromptForm(forms.ModelForm):
    """User creates Prompt details"""

    class Meta:
        model = Contest
        fields = ('prompt','wordcount','start_date','expiry_date' )
        """widgets = {
            'start_date': DateTimePickerInput(),
            'expiry_date': DateTimePickerInput(),
        }"""

class EnterContestNewStoryForm(forms.ModelForm):
    """User creates New Story to enter contest"""
    class Meta:
        model = Entry
        fields = ()

    def __init__(self, *args, **kwargs):
        self.story_wordcount = kwargs.pop('story_wordcount')
        self.contest_wordcount = kwargs.pop('contest_wordcount')
        super(EnterContestNewStoryForm, self).__init__(*args, **kwargs)

    def clean(self):
      # check if wordcount is excessive

        if self.story_wordcount > self.contest_wordcount:
            raise forms.ValidationError("More words than wordcount. Kill your darlings!")
        return self.cleaned_data  # never forget this! ;o)        
