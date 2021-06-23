"""
Models for public activities

minidome: public fight between two stories

"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from tinymce import models as tinymce_models

from baseapp.models import Story
from promptarena.models import Contest



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
    content =  tinymce_models.HTMLField(blank = True)
    battle_date = models.DateTimeField(auto_now_add=True,)
    minidome_type = models.PositiveSmallIntegerField(
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
        """Save the minidome record"""
        super(MiniDome, self).save()
        #update StoryStats appropriately (this is the only place it happens so we won't use a signal)
        # pylint: disable=no-member
        if self.minidome_type == MiniDome.LOGGED_IN:
            self.winner.stats.minidome_logged_in_wins += 1
            self.loser.stats.minidome_logged_in_losses += 1
        if self.minidome_type == MiniDome.PUBLIC:
            self.winner.stats.minidome_public_wins += 1
            self.loser.stats.minidome_public_losses += 1
        self.winner.stats.save()
        self.loser.stats.save()

class Notification(models.Model):
    class Category (models.TextChoices):
        CONTEST_ANNOUNCE_INTERNAL_JUDGE = 'CAIJ', _('Internal Judge Contest Annouce')
        CONTEST_ANNOUNCE_EXTERNAL_JUDGE = 'EJCA', _('External Judge Contest Announce')
        CONTEST_CLOSE = 'CC', _('Contest Close')
        CONTEST_RESULTS = 'CR', _('Contest Results')
        BRAWL_ASK = 'BA', _('Brawl Challenge')
        BRAWL_ACCEPTANCE = 'BA', _('Brawl Acceptance')
        BRAWL_CLOSE = 'B', _('Brawl Close')
        BRAWL_RESULT = 'BR', _('Brawl Result')
        SYSTEM = "S", _('System')

    category = models.CharField(
        max_length= 4,
        choices=Category.choices,
        default = Category.SYSTEM
    )

    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name = 'contest',
        blank = True
    )

    content =  tinymce_models.HTMLField(blank = True)
    created = models.DateTimeField(auto_now_add=True,)



