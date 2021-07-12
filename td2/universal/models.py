"""
Models for public activities

minidome: public fight between two stories

"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from tinymce import models as tinymce_models

#from baseapp.models import Story


# Create your models here.

def create_html_link(link, text):
    link = "<a href='" + link + "'>" + text + "</a>"
    return link


class MiniDome(models.Model):
    """simple table to show each battle"""
    LOGGED_IN = 1
    PUBLIC = 2
    CATEGORY_CHOICES = (
        (LOGGED_IN, 'LOGGED-IN - users of taste and distinction'),
        (PUBLIC, 'PUBLIC - the great unwashed'),
    )
    #For winner and loser we use the quoted names as importing Story leads to circular imports
    winner = models.ForeignKey(
        "baseapp.Story",
        on_delete=models.CASCADE,
        related_name = 'winner',
    )
    loser = models.ForeignKey(
        "baseapp.Story",
        on_delete=models.CASCADE,
        related_name = 'loser',
    )
    content =  tinymce_models.HTMLField(blank = True)
    battle_date = models.DateTimeField(auto_now_add=True,)
    category = models.PositiveSmallIntegerField(
        verbose_name='Category',
        default = PUBLIC,
        choices = CATEGORY_CHOICES)

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
        if self.category == MiniDome.LOGGED_IN:
            self.winner.stats.minidome_logged_in_wins += 1
            self.loser.stats.minidome_logged_in_losses += 1
        if self.category == MiniDome.PUBLIC:
            self.winner.stats.minidome_public_wins += 1
            self.loser.stats.minidome_public_losses += 1
        self.winner.stats.save()
        self.loser.stats.save()

class Notice(models.Model):
    class Category (models.TextChoices):
        CONTEST_ANNOUNCE_INTERNAL_JUDGE = 'CAIJ', _('Internal Judge Contest Annouce')
        CONTEST_ANNOUNCE_EXTERNAL_JUDGE = 'CAEJ', _('External Judge Contest Announce')
        CONTEST_CLOSE = 'CC', _('Contest Close')
        CONTEST_RESULTS = 'CR', _('Contest Results')
        BRAWL_CHALLENGE = 'BCHA', _('Brawl Acceptance')
        BRAWL_ACCEPT = 'BACC', _('Brawl Acceptance')
        BRAWL_ANNOUNCE = 'BA', _('Brawl Challenge')
        BRAWL_CLOSE = 'BC', _('Brawl Close')
        BRAWL_RESULT = 'BR', _('Brawl Result')
        STORY_ANNOUNCE = 'SA', _('Story Announce')
        SYSTEM = "SYS", _('System')

    category = models.CharField(
        max_length= 4,
        choices=Category.choices,
        default = Category.SYSTEM
    )

    LOGGED_IN = 1
    PUBLIC = 2
    PRIVACY_CHOICES = (
        (LOGGED_IN, 'LOGGED-IN - users of taste and distinction'),
        (PUBLIC, 'PUBLIC - the great unwashed'),
    )


    privacy = models.PositiveSmallIntegerField(
        choices=PRIVACY_CHOICES,
        default = LOGGED_IN
    )



    content =  tinymce_models.HTMLField(blank = True)
    created = models.DateTimeField(auto_now_add=True,)

    def __str__(self):
        """returns string name"""
        return self.category.Category.label

    #def save(self, *args, **kwargs):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, story=None, contest=None):
        """Save the notice"""
        if story:
            link = create_html_link(story.get_absolute_url(), story.title) + " by " + create_html_link(story.author.get_absolute_url(), str(story.author))
            if story.access == 2:
                self.privacy = self.PUBLIC
                self.content = link + " has just been released for everyone to read."
            elif story.access == 1:
                self.privacy = self.LOGGED_IN
                self.content = link + " has just been released for members to read."
            else:
                return
        if contest:
            link = create_html_link(contest.get_absolute_url(), contest.title)
            self.privacy = self.PUBLIC
            self.content = link + " is now open for sign-ups."

        super(Notice, self).save()





