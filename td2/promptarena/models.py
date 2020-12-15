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
    slug = AutoSlugField(max_length=200, default='no-prompt-slug', unique=True)

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
    prompt = models.ForeignKey(Prompt, null=True, on_delete=models.SET_NULL)
    start_date = models.DateTimeField('Start Date')
    expiry_date = models.DateTimeField('Submit by Date')
    title = models.CharField(max_length=200, editable=False, null=True)
    slug = AutoSlugField(max_length=200, default='no-contest-slug', unique=True)

    def __str__(self):
        if not self.title is None:
            return self.title
        return "ALERT - somehow this contest did not get set a title"

    def is_active(self):
        '''returns true if sxpiry date is passed'''
        return self.expiry_date > timezone.now()

    #def save(self, *args, **kwargs):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        slug = self.slug
        if not self.id or slug == 'no-contest-slug' or slug=='':
            self.slug = slugify(self.prompt.title)
        self.title = self.prompt.title
        super(Contest, self).save()

"""class Story(models.Model):
    ""Story - the heart of it all""
    author = models.ForeignKey(
      get_user_model(),
      on_delete=models.SET_NULL,
      null=True
    )
    prompt = models.ForeignKey(Prompt, null=True, on_delete=models.SET_NULL)
    contest = models.ForeignKey(Contest, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200, default='no story title')
    content = models.TextField(max_length=20000)
    contest_score = models.DecimalField(max_digits=5, decimal_places=2,default=0)
    public_score = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    creation_date = models.DateTimeField('date created', auto_now_add=True,)
    public_view_allowed = models.BooleanField()
    slug = models.SlugField(max_length=20, default='no-story-slug', unique=True, blank=True)

    #def save(self, *args, **kwargs):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        '''provides a story slug is one is missed'''
        slug = self.slug
        if not self.id or slug == 'no-story-slug' or slug=='':
            self.slug = slugify(self.title)
        super(Story, self).save()

    def __str__(self):
        '''sits up and says hello'''
        return self.title
"""