"""BASE reference models used across multiple apps"""
from django.db import models
#from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from autoslug import AutoSlugField

# Create your models here.
class Story(models.Model):
    """Story - the heart of it all"""
    author = models.ForeignKey(
      get_user_model(),
      on_delete=models.SET_NULL,
      null=True
    )
    title = models.CharField(max_length=200, default='no story title')
    content = models.TextField(max_length=20000)
    creation_date = models.DateTimeField('date created', auto_now_add=True,)
    public_view_allowed = models.BooleanField()
    slug = AutoSlugField(max_length=40, default='no-story-slug', unique=True, blank=True)
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
