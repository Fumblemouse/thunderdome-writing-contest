"""BASE reference models used across multiple apps"""
import re
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.html import strip_tags
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

from autoslug import AutoSlugField
from tinymce import models as tinymce_models
#from td2 import settings


# Create your models here.
class Story(models.Model):
    """Story - the heart of it all
    defines:
        _Str_
        save
        get_absolute_url
    """
    PRIVATE = 0
    LOGGED_IN = 1
    PUBLIC = 2
    ACCESS_CHOICES = (
        (PRIVATE, 'PRIVATE - Only your darkest heart'),
        (LOGGED_IN, 'LOGGED-IN - users of taste and distinction'),
        (PUBLIC, 'PUBLIC - Admit the great unwashed'),
    )
    author = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.SET_NULL,
      null=True,
      related_name = 'stories'
    )
    title = models.CharField(max_length=255)
    content =  tinymce_models.HTMLField()
    ACCESS_CHOICES = ACCESS_CHOICES
    access = models.PositiveSmallIntegerField(
        verbose_name='Who can see your story?',
        help_text = 'Caution: Making your story non-private will exclude it from entering contests',
        default = PRIVATE,
        choices = ACCESS_CHOICES)
    slug = AutoSlugField(max_length=40, unique=True)
    wordcount = models.PositiveSmallIntegerField()
    has_been_public = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True,)
    modified_date = models.DateTimeField(auto_now=True)
    #tags = models.JSONField(blank=True, null=True)
    #public_scores = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "stories"
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'], name='unique_titles_for_authors')
        ]

    def __str__(self):
        '''sits up and says hello'''
        return self.title

    #def save(self, *args, **kwargs):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Additional field input"""
        #provides a slug is one is missed
        slug = self.slug
        slugified = slugify(self.title)
        if slug != slugified:
            self.slug = slugified
        #set flag if saved for public view
        if self.access > 0:
            self.has_been_public = True

        #Add wordcount
        content = self.content
        words_to_count = strip_tags(content)
        wordcount = len(re.findall(r'\w+', words_to_count))
        self.wordcount = wordcount
        return super(Story, self).save()

    def get_absolute_url(self):
        """Returns a permalink for the story"""
        return reverse('view story by slug', kwargs = { 'author_slug': self.author.slug , 'story_slug' : self.slug, })

@receiver(post_save, sender=Story)
def ensure_story_stats_exist(sender, **kwargs):
    """Create storyStat on creation of story if one doesn't exist"""
    if kwargs.get('created', False):
        StoryStats.objects.get_or_create(story=kwargs.get('instance'))



class StoryStats(models.Model):
    story = models.OneToOneField(
        Story,
        on_delete=models.CASCADE,
        related_name = 'stats',
        primary_key=True
    )
    minidome_public_wins = models.PositiveSmallIntegerField( default = 0)
    minidome_public_losses = models.PositiveSmallIntegerField( default = 0)
    minidome_logged_in_wins = models.PositiveSmallIntegerField( default = 0)
    minidome_logged_in_losses = models.PositiveSmallIntegerField( default = 0)
    minidome_total_wins = models.PositiveSmallIntegerField( default = 0)
    minidome_total_losses = models.PositiveSmallIntegerField( default = 0)
    minidome_total_public_tests = models.PositiveSmallIntegerField( default = 0)
    minidome_total_logged_in_tests = models.PositiveSmallIntegerField( default = 0)
    
    class Meta:
        verbose_name_plural = "Story Stats"

    def __str__(self):
        '''sits up and says hello'''
        return "stats for " + self.story.title
    
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """increment totals"""
        self.minidome_total_wins = self.minidome_public_wins + self.minidome_logged_in_wins
        self.minidome_total_losses = self.minidome_public_losses + self.minidome_logged_in_losses
        self.minidome_total_public_tests = self.minidome_public_wins + self.minidome_public_losses
        self.minidome_total_logged_in_tests = self.minidome_logged_in_wins + self.minidome_logged_in_losses
        super(StoryStats, self).save()

