"""BASE reference models used across multiple apps"""
import re
from django.db import models
#from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils.html import strip_tags
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
    creation_date = models.DateTimeField(auto_now_add=True,)
    modified_date = models.DateTimeField(auto_now=True)
    public = models.BooleanField(
        verbose_name='Show publically?',
        help_text = 'Caution: Displaying a story publcially will exclude it from future contests')
    slug = AutoSlugField(max_length=40, unique=True)
    wordcount = models.PositiveSmallIntegerField()
    has_been_public = models.BooleanField(default=False)
    #tags = models.JSONField(blank=True, null=True)
    #public_scores = models.JSONField(blank=True, null=True)

    #def save(self, *args, **kwargs):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Additional field input"""
        #provides a slug is one is missed
        slug = self.slug
        slugified = slugify(self.title)
        if not self.id or slug != slugified:
            self.slug = slugified
        #set flag if saved for public view
        if self.public:
            self.has_been_public = True

        #Add wordcount
        content = self.content
        words_to_count = strip_tags(content)
        wordcount = len(re.findall(r'\w+', words_to_count))
        self.wordcount = wordcount
        return super(Story, self).save()


    def __str__(self):
        '''sits up and says hello'''
        return self.title
    class Meta:
        verbose_name_plural = "stories"
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'], name='unique_titles_for_authors')
        ]
