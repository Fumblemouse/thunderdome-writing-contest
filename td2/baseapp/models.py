"""BASE reference models used across multiple apps"""
from django.db import models
#from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from autoslug import AutoSlugField
from tinymce import models as tinymce_models

# Create your models here.
class Story(models.Model):
    """Story - the heart of it all"""
    author = models.ForeignKey(
      get_user_model(),
      on_delete=models.SET_NULL,
      null=True
    )
    title = models.CharField(max_length=255)
    content =  tinymce_models.HTMLField()
    creation_date = models.DateTimeField('date created', auto_now_add=True,)
    modified_date = models.DateTimeField(auto_now=True)
    public_view_allowed = models.BooleanField(verbose_name='Display to non-logged in users?')
    slug = AutoSlugField(max_length=40, default='no-story-slug', unique=True)

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
    class Meta:
        verbose_name_plural = "stories"
