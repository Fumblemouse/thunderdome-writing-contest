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
    prompt = models.ForeignKey(Prompt, on_delete=models.SET_NULL, null=True) #Null = true to make on_delete work
    start_date = models.DateTimeField('Start Date')
    expiry_date = models.DateTimeField('Submit by Date')
    wordcount = models.PositiveIntegerField(default=1000)
    slug = AutoSlugField(max_length=200, default='no-contest-slug', unique=True)

    def __str__(self):
        if self.prompt:
            return self.prompt.title
        return "ALERT - somehow this contest did not get set a title"

    def is_active(self):
        '''returns true if sxpiry date is passed'''
        return self.expiry_date > timezone.now()

    #def save(self, *args, **kwargs):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        slug = self.slug
        if not self.id or slug.startswith('no-contest-') or slug=='':
            self.slug = "contest-" + slugify(self.prompt.title)
        super(Contest, self).save()

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


class Crits(models.Model):
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
    reviewer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = tinymce_models.HTMLField()
    score = models.IntegerField(choices=SCORE_CHOICES, default=UNSCORED)
