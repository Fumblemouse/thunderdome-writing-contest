"""
Models for public activities

minidome: public fight between two stories

"""
from django.db import models
from tinymce import models as tinymce_models

from baseapp.models import Story



# Create your models here.

class MiniDome(models.Model):
    """simple table to show each battle"""
    LOGGED_IN = 1
    PUBLIC = 2
    DOME_TYPE_CHOICES = (
        (LOGGED_IN, 'LOGGED-IN - users of taste and distinction'),
        (PUBLIC, 'PUBLIC - the great unwashed'),
    )
    winner = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name = 'winner',
    )
    loser = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name = 'loser',
    )
    content =  tinymce_models.HTMLField()
    battle_date = models.DateTimeField(auto_now_add=True,)
    dome_type = models.PositiveSmallIntegerField(
        verbose_name='MiniDome Type',
        default = PUBLIC,
        choices = DOME_TYPE_CHOICES)

    class Meta:
        """provides verbose name"""
        verbose_name_plural = "MiniDomes"

    def __str__(self):
        """name shows winner then loser"""
        name = self.winner.slug + " vs " + self.loser.slug
        return name

    #def save(self, *args, **kwargs):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
