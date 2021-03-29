"""
MODELS

    Prompt: Things to write about
    Contest: Base Entity with a start date and end date
    InternalJudgeContest: Contest where contestants are judges - has own ruleset
    Stories: Written using prompts to enter contests
    Entry: Bridge between story and contest
    Crit: Criticism of particular entry
"""
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from autoslug import AutoSlugField
#from tinymce.models import HTMLField
from tinymce import models as tinymce_models
from baseapp.models import Story
from baseapp.utils import sattolo_cycle

#from django.apps import apps
#Story = apps.get_model('baseapp', 'Story')

# Create your models here.

class Prompt(models.Model):
    """Prompt - push to creativity"""
    creator = models.ForeignKey(
      get_user_model(),
      on_delete=models.SET_NULL,
      null=True
    )
    title = models.CharField(max_length=200, unique= True)
    content =  tinymce_models.HTMLField()
    creation_date = models.DateTimeField(auto_now_add=True)
    slug = AutoSlugField(max_length=200, unique=True)

    def __str__(self):
        return self.title

    #def save(self, *args, **kwargs):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        slug = self.slug
        slugified = slugify(self.title)
        if not self.id or slug != slugified:
            self.slug = slugified
        return super(Prompt, self).save()

class Contest(models.Model):
    """Contest- Competition Base Class"""
    UNOPENED = 'UNOPENED'
    OPEN='OPEN'
    JUDGEMENT = 'JUDGEMENT'
    CLOSED = 'CLOSED'
    CONTEST_STATES = [
        (UNOPENED, 'Unopened'),
        (OPEN, 'Open'),
        (JUDGEMENT, 'Judgement'),
        (CLOSED, 'Closed')
    ]
    INTERNAL_JUDGE_CONTEST = "INTERNAL JUDGE CONTEST"
    BRAWL_CONTEST = "BRAWL"

    CONTEST_TYPES = [
        (INTERNAL_JUDGE_CONTEST, 'Internal Judge Contest'),
        #(BRAWL_CONTEST, 'Brawl')
    ]
    prompt = models.ForeignKey(Prompt, on_delete=models.SET_NULL, null=True) #Null = true to make on_delete work
    title = models.CharField(max_length=200, unique= True, blank=True)
    content =  tinymce_models.HTMLField()
    start_date = models.DateTimeField('Start Date')
    expiry_date = models.DateTimeField('Submit by Date')
    mode = models.CharField(choices=CONTEST_TYPES, default='INTERNAL JUDGE CONTEST', max_length=22)
    status= models.CharField(choices=CONTEST_STATES, default='UNOPENED', max_length=9)
    max_wordcount = models.PositiveIntegerField(default=1000)
    entrant_num = models.PositiveSmallIntegerField(default = 0)
    slug = AutoSlugField(max_length=200, unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.prompt:
            return self.prompt.title
        return "ALERT - somehow this contest did not get set a title"

    def is_active(self):
        '''returns true if expiry date is passed'''
        return self.expiry_date > timezone.now() > self.start_date

    #def save(self, *args, **kwargs):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        #provides a slug is one is missed
        slug = self.slug
        slugified = slugify(self.prompt.title)
        if not self.id or slug != slugified:
            self.slug = slugified
        if self.is_active() and self.status != 'JUDGEMENT' and self.status != 'CLOSED':
            self.status = 'OPEN'
        return super(Contest, self).save()

    def set_open(self):
        """Sets status to open"""
        self.status = 'OPEN'
        self.save()

    def set_judgement(self):
        """Sets status to open"""
        self.status = 'JUDGEMENT'
        self.save()

    def set_closed(self):
        """Sets status to open"""
        self.status = 'CLOSED'
        self.save()

    def get_final_crits(self):
        """returns finished crits for a given contest"""
        return Crit.objects.filter(entry__contest = self, final = True).order_by('reviewer')



class InternalJudgeContest(Contest):
    """
    Proxy Model class of Contest where judging is done by other contestants
    defines:
        close()
        judge()
        assign_stories()
        judge()
    """
    class Meta:
        proxy=True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.mode = 'INTERNAL JUDGE CONTEST'
        return super(InternalJudgeContest, self).save()

    def close(self):
        """assign stories to judges"""
        #get list of entries to this contest
        entries = Entry.objects.filter(contest = self)
        #get list of entrants and stories from entries
        stories = entries.values_list('story', flat=True)
        stories = list(stories)
        entrants = entries.values_list('story__author', flat=True)
        entrants = list(entrants)

        #setup container for creating crit requirements, fill it with [entrant [list,of,stories]]
        judges_with_stories = list()

        for entrant in entrants:
            judges_with_stories.append([entrant, []])
        loopmax = 3

        loop =1
        #breakpoint()
        while loop <= loopmax:
            shuffled_stories = sattolo_cycle(stories.copy())
            judge_temp = self.assign_stories(shuffled_stories, judges_with_stories)
            if judge_temp != "duplicate error":
                judges_with_stories = judge_temp
                loop += 1

        for judge in judges_with_stories:
            reviewer =  get_user_model().objects.get(pk = judge[0])
            for story in judge[1]:
                story_instance = Story.objects.get(pk = story)
                contest_instance = self
                entry = Entry.objects.get(contest = contest_instance, story=story_instance)
                Crit.objects.create(story = story_instance, reviewer= reviewer, entry = entry )
        self.status = 'JUDGEMENT'
        self.save()

    def assign_stories(self, shuffled_stories, judges_with_stories):
        """checks for duplicates and returns list if there are none"""
	    #test for pre-existing things
        for judge in enumerate(judges_with_stories):
            if shuffled_stories[judge[0]] in judges_with_stories[judge[0]][1]:
                return "duplicate error"
        #nothing pre-existing - merge the array
        for story in enumerate(judges_with_stories):
            judges_with_stories[story[0]][1].append(shuffled_stories[story[0]])
        return judges_with_stories

    def judge(self):
        """Count, Sort the results and close the contest"""
        crits = Crit.objects.filter(entry__contest__pk = self.pk)
        results = {}
        results_order = {}
        #previous score is used to track multiple entries with the same score
        previous_score = 0
        #additive determines placing.  Multiple 1sts means next lowest is 2nd
        additive = 1
        #create a dictionary with entry as key and an array of scores from judges
        for crit in crits:
            results.setdefault(crit.entry, [])
            results[crit.entry].append(crit.score)

        #sort the dictionary based on sum of the scores array (descending)
        results_order = sorted(results.items(), key=lambda x: sum(x[1]), reverse=True)
        #Create a result record for each item in the sorted array
        for count, result in enumerate(results_order):
            entry = Entry.objects.get(pk = result[0].pk)
            if previous_score != sum(result[1]):
                entry.position = count + additive
            else:
                additive -= 1
                entry.position = count + additive

            entry.score = sum(result[1])
            previous_score = sum(result[1])
            if entry.position == 1:
                entry.story.author.wins += 1
            elif entry.position == 2:
                entry.story.author.hms += 1
            elif entry.position == (results_order.length + additive)-1:
                entry.story.author.dms += 1
            elif entry.position == results_order.length + additive:
                entry.story.author.losses += 1    
            entry.save()
            #add result to profile
            

        self.entrant_num = len(results)
        self.status = 'CLOSED'
        self.save()

class BrawlContest(Contest):
    """
    Child class of Contest where judging is done by other contestants
    defines:
        close()
        judge()
        assign_stories()
        judge()
    """
    class Meta:
        proxy = True

    def close(self):
        """assign stories to judges"""
        #get list of entries to this contest
        entries = Entry.objects.filter(contest = self)
        #get list of entrants and stories from entries
        stories = entries.values_list('story', flat=True)
        stories = list(stories)
        entrants = entries.values_list('story__author', flat=True)
        entrants = list(entrants)

        #setup container for creating crit requirements, fill it with [entrant [list,of,stories]]
        judges_with_stories = list()

        for entrant in entrants:
            judges_with_stories.append([entrant, []])
        loopmax = 3

        loop =1
        #breakpoint()
        while loop <= loopmax:
            shuffled_stories = sattolo_cycle(stories.copy())
            judge_temp = self.assign_stories(shuffled_stories, judges_with_stories)
            if judge_temp != "duplicate error":
                judges_with_stories = judge_temp
                loop += 1

        for judge in judges_with_stories:
            reviewer =  get_user_model().objects.get(pk = judge[0])
            for story in judge[1]:
                story_instance = Story.objects.get(pk = story)
                contest_instance = self
                entry = Entry.objects.get(contest = contest_instance, story=story_instance)
                Crit.objects.create(story = story_instance, reviewer= reviewer, entry = entry )
        self.status = 'JUDGEMENT'
        self.save()

    def assign_stories(self, shuffled_stories, judges_with_stories):
        """checks for duplicates and returns list if there are none"""
	    #test for pre-existing things
        for judge in enumerate(judges_with_stories):
            if shuffled_stories[judge[0]] in judges_with_stories[judge[0]][1]:
                return "duplicate error"
        #nothing pre-existing - merge the array
        for story in enumerate(judges_with_stories):
            judges_with_stories[story[0]][1].append(shuffled_stories[story[0]])
        return judges_with_stories

    def judge(self):
        """Count, Sort the results and close the contest"""
        crits = Crit.objects.filter(entry__contest__pk = self.pk)
        results = {}
        results_order = {}
        #create a dictionary with entry as key and an array of scores from judges
        for crit in crits:
            results.setdefault(crit.entry, [])
            results[crit.entry].append(crit.score)

        #sort the dictionary based on sum of the scores array (descending)
        results_order = sorted(results.items(), key=lambda x: sum(x[1]), reverse=True)
        #Create a result record for each item in the sorted array
        for count, result in enumerate(results_order):
            entry = Entry.objects.get(pk = result[0].pk)
            entry.position = count + 1
            entry.score = sum(result[1])
            entry.save()
        self.entrant_num = len(results)
        self.status = 'CLOSED'
        self.save()

class Entry(models.Model):
    """Links stories and contests"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    #NB - this is referring to the baseclass Contest, which means there are joins in any query
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField(default=0)
    score = models.PositiveSmallIntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    content =  tinymce_models.HTMLField()

    def __str__(self):
        if self.story and self.contest:
            return str(self.story.author) + " : " + self.title
        return "ALERT - somehow this entry did not get set a title"

    class Meta:
        verbose_name_plural = "entries"


class Crit(models.Model):
    """Reviews of stories"""
    UNSCORED = 0
    LOW_SCORE = 3
    LOW_MID_SCORE = 5
    MID_SCORE = 7
    HI_MID_SCORE = 11
    HI_SCORE = 13
    SCORE_CHOICES = [
        (UNSCORED, 'Select Score'),
        (LOW_SCORE, 'Low'),
        (LOW_MID_SCORE, 'Low Middle'),
        (MID_SCORE, 'Middle'),
        (HI_MID_SCORE, 'High Middle'),
        (HI_SCORE, 'High')
    ]
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.SET_NULL, null=True)
    reviewer = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    content = tinymce_models.HTMLField(help_text='Please enter your comments here')
    score = models.IntegerField(choices=SCORE_CHOICES, default=UNSCORED)
    final = models.BooleanField(
        blank = True,
        default=False,
        help_text="Check this box if you are finished with your critique. Be warned! - once submitted with this box checked no further edits can be made."
    )
    wordcount = models.PositiveIntegerField(default=100, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.reviewer and self.entry:
            return str(self.entry.contest.prompt.title) + " : " + str(self.reviewer.username) + " reviews " + str(self.story.author.username) # pylint: disable=E1101
        return "ALERT - somehow this crit did not get set a title"
