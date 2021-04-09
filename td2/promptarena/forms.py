"""Describes custom forms"""
import re
from django.utils import timezone
from django import forms
from django.utils.html import strip_tags
#from django.utils.translation import gettext_lazy as _
from baseapp.forms import BaseForm
from baseapp.models import Story



#from flatpickr import DateTimePickerInput

from .models import Contest, Entry, Crit

class CreateContestForm(BaseForm):
    """User creates Prompt details"""

    class Meta:
        model = Contest
        fields = ('title', 'content', 'max_wordcount', 'start_date','expiry_date' )

class CopyContestForm(BaseForm):
    """User creates Prompt details"""

    class Meta:
        model = Contest
        fields = ('title', 'content','max_wordcount','start_date','expiry_date' )

class ContestStoryForm(BaseForm):
    """User enters Story and Title"""

    class Meta:
        model = Story
        fields = ('title', 'content')

class EnterContestNewStoryForm(BaseForm):
    """User creates New Story to enter contest"""
    class Meta:
        model = Entry
        fields = ()

    def __init__(self, *args, **kwargs):
        self.story_wordcount = kwargs.pop('story_wordcount')
        self.contest_max_wordcount = kwargs.pop('contest_max_wordcount')
        self.expiry_date = kwargs.pop('contest_expiry_date')
        super(EnterContestNewStoryForm, self).__init__(*args, **kwargs)

    def clean(self):
        # check if wordcount is excessive
        if self.story_wordcount > self.contest_max_wordcount:
            raise forms.ValidationError("More words than wordcount. Kill your darlings!")
        # check if expiry date is past
        if self.expiry_date < timezone.now():
            raise forms.ValidationError("The deadline for that contest is over.")
        return self.cleaned_data  # never forget this! ;o)

class EnterContestOldStoryForm(BaseForm):
    """User recycles old Story to enter contest"""
    class Meta:
        model = Entry
        fields = ('story',)

    def __init__(self, *args, **kwargs):
        self.story_wordcount = kwargs.pop('story_wordcount')
        self.contest_max_wordcount = kwargs.pop('contest_max_wordcount')
        self.expiry_date = kwargs.pop('contest_expiry_date')
        super(EnterContestOldStoryForm, self).__init__(*args, **kwargs)

    def clean(self):
        # check if wordcount is excessive
        if self.story_wordcount > self.contest_max_wordcount:
            raise forms.ValidationError("More words than wordcount. Kill your darlings!")
        # check if expiry date is past
        if self.expiry_date < timezone.now():
            raise forms.ValidationError("The deadline for that contest is over.")
        return self.cleaned_data  # never forget this! ;o)

class EnterCritForm(BaseForm):
    """user enters comments and score for story"""
    class Meta:
        model = Crit
        fields = ('content', 'score', 'final')
        labels = {
           # 'content': _('Critique'),
        }

    def __init__(self, *args, **kwargs):
        """Init For: defines wordcount initially"""
        self.wordcount = 0
        super(EnterCritForm, self).__init__(*args, **kwargs)

    def clean(self):
      # check if wordcount is excessive
        crit_wordcount_min = 10
        cleaned_data = super().clean()
        words_to_count = strip_tags(cleaned_data.get('content'))
        crit_wordcount = len(re.findall(r'\S+', words_to_count))
        self.wordcount = crit_wordcount
        if self.wordcount < crit_wordcount_min:
            raise forms.ValidationError("Entrants deserve at least " + str(crit_wordcount_min = 10) + " words for their efforts!" )
        if cleaned_data.get('score') == 0 and cleaned_data.get('final'):
            raise forms.ValidationError("You can't submit a final judgement without a score." )
        return self.cleaned_data  # never forget this! ;o)
