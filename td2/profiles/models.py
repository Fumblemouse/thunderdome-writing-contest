"""Models from profiles app"""
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from autoslug import AutoSlugField
from tinymce import models as tinymce_models


class CustomUser(AbstractUser):
    """Custom user assists extendability of user without additional joins to a profile table """
    # add additional fields in here
    PRIVATE = 0
    LOGGED_IN = 1
    PUBLIC = 2
    ACCESS_CHOICES = (
        (PRIVATE, 'PRIVATE: Only your darkest heart'),
        (LOGGED_IN, 'LOGGED-IN: Fellow users of taste and distinction'),
        (PUBLIC, 'PUBLIC: The great unwashed'),
    )
    bio = tinymce_models.HTMLField(blank=True, )
    private_profile = models.BooleanField(
        default=False,
        help_text='Check this to keep your work private from anyone except your fellow contestants.',
        verbose_name='Private profile',
    )
    highest_access = models.PositiveSmallIntegerField(
        verbose_name='Restrict Story Sharing to:',
        help_text = 'Setting a value here will restrict all your stories to that \
                    level of privacy or more private. Eg, Selecting LOGGED-IN will make all of your PUBLIC \
                    stories only available to logged in users and prevent individual stories being set any higher. \
                    If this field is later set to a higher setting, individual stories \
                    will need their own privacy settings increased. Stories are Private by default',
        default = PUBLIC,
        choices = ACCESS_CHOICES)

    timezone = models.CharField(default="Pacific/Auckland", max_length=100)
    slug = AutoSlugField(max_length=200)
    wins = models.PositiveSmallIntegerField( default = 0)
    losses = models.PositiveSmallIntegerField( default = 0)
    hms = models.PositiveSmallIntegerField( default = 0)
    dms = models.PositiveSmallIntegerField( default = 0)
    brawl_wins = models.PositiveSmallIntegerField( default = 0)
    brawl_losses = models.PositiveSmallIntegerField( default = 0)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        slug = self.slug
        slugified = slugify(self.username)
        if not self.pk or slug != slugified:
            self.slug = slugified
        return super(CustomUser, self).save()
