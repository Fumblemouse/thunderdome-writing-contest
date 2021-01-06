"""
MODELS

Prompt: Things to write about
Contest: Entity with a start date and end date
Stories: Written using prompts to enter contests
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
    creation_date = models.DateTimeField( 'date created', auto_now_add=True)
    slug = AutoSlugField(max_length=200, unique=True)

    def __str__(self):
        return self.title

    #def save(self, *args, **kwargs):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        slug = self.slug
        if not self.id or slug == 'no-prompt-slug' or slug=='':
            self.slug = slugify(self.title)
        super(Prompt, self).save()

class Contest(models.Model):
    """Contest- Actual Competition"""
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
    prompt = models.ForeignKey(Prompt, on_delete=models.SET_NULL, null=True) #Null = true to make on_delete work
    start_date = models.DateTimeField('Start Date')
    expiry_date = models.DateTimeField('Submit by Date')
    status= models.CharField(choices=CONTEST_STATES, default='Unopened', max_length=9)
    wordcount = models.PositiveIntegerField(default=1000)
    slug = AutoSlugField(max_length=200, default='no-contest-slug', unique=True)

    def __str__(self):
        if self.prompt:
            return self.prompt.title
        return "ALERT - somehow this contest did not get set a title"

    def is_active(self):
        '''returns true if expiry date is passed'''
        return self.expiry_date > timezone.now() > self.start_date

    #def save(self, *args, **kwargs):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        slug = self.slug
        if not self.id or slug.startswith('no-contest-') or slug=='':
            self.slug = "contest-" + slugify(self.prompt.title)
        super(Contest, self).save()

    def close(self):
        """assign stories to judges"""
        #get list of entries to this contest
        entries = Entry.objects.all().filter(contest = self)
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
            if judge_temp == "error":
                print(judges_with_stories)
            else:
                judges_with_stories = judge_temp
                loop += 1

        for judge in judges_with_stories:
            reviewer =  get_user_model().objects.get(pk = judge[0])
            for story in judge[1]:
                story_instance = Story.objects.get(pk = story)
                Crit.objects.create(contest = self, reviewer= reviewer, story = story_instance )

    def assign_stories(self, shuffled_stories, judges_with_stories):
        """checks for duplicates and returns list if there are none"""
	    #test for pre-existing things
        for judge in enumerate(judges_with_stories):
            if shuffled_stories[judge[0]] in judges_with_stories[judge[0]][1]:
                return "error"
        #nothing pre-existing - merge the array
        for story in enumerate(judges_with_stories):
            judges_with_stories[story[0]][1].append(shuffled_stories[story[0]])
        return judges_with_stories



class Entry(models.Model):
    """Links stories and contests"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    contest_scores = models.CharField(blank=True, max_length=200)

    def __str__(self):
        if self.story and self.contest:
            return str(self.story.author) + " : " + self.contest.prompt.title
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
    contest = models.ForeignKey(Contest, on_delete=models.SET_NULL, null=True)
    reviewer = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    content = tinymce_models.HTMLField(help_text='Please enter your comments here')
    score = models.IntegerField(choices=SCORE_CHOICES, default=UNSCORED)
    final = models.BooleanField(blank = True, default=False)

    def __str__(self):
        if self.reviewer and self.contest:
            return str(self.contest.prompt.title) + " : " + str(self.reviewer.username) + " reviews " + str(self.story.author) # pylint: disable=E1101
        return "ALERT - somehow this crit did not get set a title"
