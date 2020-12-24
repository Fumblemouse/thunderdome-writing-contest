"""Describes custom forms"""
from django import forms
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