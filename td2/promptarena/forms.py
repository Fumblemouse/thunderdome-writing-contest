"""Describes custom forms"""
import re
from django.utils import timezone
from django import forms
from django.shortcuts import get_object_or_404
from django.utils.html import strip_tags

#from django.utils.translation import gettext_lazy as _
from baseapp.forms import BaseForm
from baseapp.models import Story



#from flatpickr import DateTimePickerInput

from .models import Contest, Entry, Crit, ContestJudges

class CreateContestForm(BaseForm):
    """User creates contest details"""

    class Meta:
        model = Contest
        fields = ('title', 'content', 'max_wordcount', 'start_date','expiry_date' )

    def clean(self):
        cleaned_data = super().clean()
        expiry = cleaned_data.get("expiry_date")
        start = cleaned_data.get("start_date")

        if expiry <= start:
            raise forms.ValidationError("That contest will end before it even begins.")
        if start + timezone.timedelta(days=1) > expiry:
            raise forms.ValidationError("There must be 24 hours between start and end date.")
        return self.cleaned_data  # never forget this! ;o)

class EditContestForm(BaseForm):
    """User creates contest details"""

    class Meta:
        model = Contest
        fields = ('title', 'content','max_wordcount','start_date','expiry_date' )



class AddJudgeForm(BaseForm):
    """User adds a judge to a contest"""
    class Meta:
        model = ContestJudges
        fields = ('judge',)

    def __init__(self, *args, **kwargs):
        """Set up the contest from the additional kwargs"""
        #note we are passing an int id as contest_id from the keyword arguments
        self.contest = get_object_or_404(Contest, pk = kwargs.pop('contest_id'))
        self.cleaned_data = None #define here for pylint tidyness
        super(AddJudgeForm, self).__init__(*args, **kwargs)

    def clean(self):
        # NB - we have to test this in the view as the contest is addded after validation
        self.cleaned_data = super().clean()
        judge = self.cleaned_data.get('judge')
        chief_judge = self.contest.creator

        #print(judge, chief_judge)
        if judge == chief_judge:
            raise forms.ValidationError('Contest creator is alrady a judge!')

        judge_count = ContestJudges.objects.filter(contest = self.contest.pk, judge = judge.pk).count()
        if judge_count >= 1:
            raise forms.ValidationError('This judge is already judging this contest')
        return self.cleaned_data  # never forget this! ;o)


class ContestStoryForm(BaseForm):
    """User enters Story and Title
    TODO: is this needed still?"""

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
        self.wordcount_min = 10
        super(EnterCritForm, self).__init__(*args, **kwargs)

    def clean(self):
      # check if wordcount is excessive
        cleaned_data = super().clean()
        words_to_count = strip_tags(cleaned_data.get('content'))
        crit_wordcount = len(re.findall(r'\S+', words_to_count))
        self.wordcount = crit_wordcount
        if self.wordcount < self.wordcount_min:
            raise forms.ValidationError("Entrants deserve at least " + str(self.wordcount_min) + " words for their efforts!" )
        if cleaned_data.get('score') == 0 and cleaned_data.get('final'):
            raise forms.ValidationError("You can't submit a final judgement without a score." )
        return self.cleaned_data  # never forget this! ;o)
