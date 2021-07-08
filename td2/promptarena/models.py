"""
MODELS

    Contest: Base Entity with a start date and end date
    InternalJudgeContest: Contest where contestants are judges - has own ruleset
    Stories: Written using prompts to enter contests
    Entry: Bridge between story and contest
    Crit: Criticism of particular entry
    ContestJudges: List of judges for a given contest (can be none or many)
"""
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
from django.urls import reverse

from tinymce import models as tinymce_models
from baseapp.models import Story
from baseapp.utils import sattolo_cycle
from autoslug import AutoSlugField


# Create your models here.

class Contest(models.Model):
    """Contest- Competition Base Class"""
    UNOPENED = 0
    OPEN = 1
    JUDGEMENT = 2
    CLOSED = 3
    STATES = [
        (UNOPENED, 'Unopened'),
        (OPEN, 'Open for sign-ups'),
        (JUDGEMENT, 'Judgement'),
        (CLOSED, 'Closed')
    ]
    INTERNAL_JUDGE_CONTEST = "IC"
    EXTERNAL_JUDGE_CONTEST = "EC"
    BRAWL = "BC"

    CATEGORIES = [
        (INTERNAL_JUDGE_CONTEST, 'Rumble'),
        (EXTERNAL_JUDGE_CONTEST, 'Judges'),
        (BRAWL, 'Brawl')
    ]
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name = 'contests'
    )
    title = models.CharField(max_length=200, unique= True, blank=True)
    content =  tinymce_models.HTMLField()
    judges = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ContestJudges",
        blank= True
        )
    start_date = models.DateTimeField('Start Date')
    expiry_date = models.DateTimeField('Submit by Date')
    mode = models.CharField(choices=CATEGORIES, default=INTERNAL_JUDGE_CONTEST, max_length=2)
    status= models.PositiveSmallIntegerField(choices=STATES, default=UNOPENED)
    max_wordcount = models.PositiveIntegerField(default=1000)
    entrant_num = models.PositiveSmallIntegerField(default = 0)
    slug = AutoSlugField(max_length=200, unique=True)
    creation_date = models.DateTimeField(auto_now_add=True,)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    #def save(self, *args, **kwargs):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        #provides a slug is one is missed
        slug = self.slug
        slugified = slugify(self.title)
        if not self.id or slug != slugified:
            self.slug = slugified
        if self.is_active() and self.status != Contest.JUDGEMENT and self.status != Contest.CLOSED:
            self.status = Contest.OPEN
        return super(Contest, self).save()

    def is_active(self):
        '''returns true if datenow between start and finish'''
        return self.expiry_date > timezone.now() > self.start_date

    def set_status(self, status):
        """set status programatically"""
        self.status = status
        self.save()

    def get_final_crits(self):
        """returns finished crits for a given contest"""
        return Crit.objects.filter(entry__contest = self, final = True).order_by('reviewer')

    def get_absolute_url(self):
        """returns permalink for  a given contest"""
        return reverse('view contest details', kwargs = { 'contest_id': self.pk  })



class InternalJudgeContest(Contest):
    """
    Proxy Model class of Contest where judging is done by other contestants
    defines:
        close()
        judge()
        assign_stories()
        judge()
    """
    class Meta:
        proxy=True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.mode = 'INTERNAL JUDGE CONTEST'
        return super(InternalJudgeContest, self).save()

    def close(self):
        """assign stories to judges"""
        #get list of entries to this contest
        entries = Entry.objects.filter(contest = self)

        #setup container for creating crit requirements, fill it with [entrant [list,of,stories]]
        judges_with_entries = list()

        for entry in entries:
            judges_with_entries.append([entry, []])
        loopmax = 3

        loop =1
        #breakpoint()
        while loop <= loopmax:
            shuffled_entries = sattolo_cycle(list(entries).copy())
            judge_temp = self.assign_entries(shuffled_entries, judges_with_entries)
            if judge_temp != "duplicate error":
                judges_with_entries = judge_temp
                loop += 1
        #print(judges_with_entries)
        for judge in judges_with_entries:

            reviewer =  judge[0].story.author

            for entry in judge[1]:
                Crit.objects.create(entry = entry, reviewer= reviewer )
        self.status = Contest.JUDGEMENT
        self.save()

    def assign_entries(self, shuffled_entries, judges_with_entries):
        """checks for duplicates and returns list if there are none"""
	    #test for pre-existing things
        for judge in enumerate(judges_with_entries):
            if shuffled_entries[judge[0]] in judges_with_entries[judge[0]][1]:
                return "duplicate error"
        #nothing pre-existing - merge the array
        for entry in enumerate(judges_with_entries):
            judges_with_entries[entry[0]][1].append(shuffled_entries[entry[0]])
        return judges_with_entries

    def judge(self):
        """Count, Sort the results and close the contest"""
        crits = Crit.objects.filter(entry__contest = self)
        results = {}
        results_order = {}
        #previous score is used to track multiple entries with the same score
        previous_score = 0
        #additive determines placing.  Multiple 1sts means next lowest is 2nd
        additive = 1
        #create a dictionary with entry as key and an array of scores from judges
        for crit in crits:
            results.setdefault(crit.entry, [])
            results[crit.entry].append(crit.score)

        #sort the dictionary based on sum of the scores array (descending)
        results_order = sorted(results.items(), key=lambda x: sum(x[1]), reverse=True)
        #Create a result record for each item in the sorted array
        for count, result in enumerate(results_order):
            score = sum(result[1])
            entry = Entry.objects.get(pk = result[0].pk)
            if previous_score == score:
                additive -= 1
            entry.position = count + additive

            entry.score = score
            entry.save()
            previous_score = score

        #add result to profile once placings are assigned
        for result in results_order:

            entry = Entry.objects.get(pk = result[0].pk)
            if entry.position == 1:
                entry.author.wins += 1
                entry.author.save()
                #print('win: ', entry.position)
            elif entry.position == 2:
                entry.author.hms += 1
                entry.author.save()
                #print('hm: ', entry.position)
            elif entry.position == (len(results_order) + additive)-2:
                entry.author.dms += 1
                entry.author.save()
                #print('dm: ', entry.position)
            elif entry.position == (len(results_order) + additive)-1:
                entry.author.losses += 1
                entry.author.save()
                #print('loss: ', entry.position)

        self.entrant_num = len(results)
        self.status = Contest.CLOSED
        self.save()

class ExternalJudgeContest(Contest):
    """
    Child class of Contest where judging is done by other contestants
    defines:
        close()
        judge()
        assign_stories()
        judge()
    """
    class Meta:
        proxy = True

    def close(self):
        """assign stories to judges"""
        #get list of entries to this contest
        entries = Entry.objects.filter(contest = self)
        judges = list(self.judges.all())
        judges.append(self.creator)

        #setup container for creating crit requirements, fill it with [entrant [list,of,stories]]

        for judge in judges:
            #judges_with_stories.append([judge, []])
            shuffled_entries = sattolo_cycle(list(entries).copy())
            for entry in shuffled_entries:
                Crit.objects.create(entry = Entry.objects.get(pk = entry.id), reviewer = judge )
        self.status = Contest.JUDGEMENT
        self.save()


    def judge(self):
        """Count, Sort the results and close the contest"""
        crits = Crit.objects.filter(entry__contest__pk = self.pk)
        results = {}
        results_order = {}
        #create a dictionary with entry as key and an array of scores from judges
        for crit in crits:
            results.setdefault(crit.entry, [])
            results[crit.entry].append(crit.score)

        #sort the dictionary based on sum of the scores array (descending)
        results_order = sorted(results.items(), key=lambda x: sum(x[1]), reverse=True)
        #Create a result record for each item in the sorted array
        for count, result in enumerate(results_order):
            entry = Entry.objects.get(pk = result[0].pk)
            entry.position = count + 1
            entry.score = sum(result[1])
            entry.save()
        self.entrant_num = len(results)
        self.status = Contest.CLOSED
        self.save()

class Brawl(Contest):
    """
    Child class of Contest where judging is done by one judge
    defines:
        close()
        judge()
    """
    class Meta:
        proxy = True

    def close(self):
        """assign stories to judges"""
        #get list of entries to this contest
        entries = Entry.objects.filter(contest = self)
        #setup container for creating crit requirements, fill it with [entrant [list,of,stories]]
        for entry in entries:
            Crit.objects.create(entry = Entry.objects.get(pk = entry.id), reviewer = self.creator )
        self.status = Contest.JUDGEMENT
        self.save()


    def judge(self):
        """Count, Sort the results and close the contest"""
        crits = Crit.objects.filter(entry__contest__pk = self.pk)

        results = {}
        results_order = {}
        #create a dictionary with entry as key and an array of scores from judges
        for crit in crits:
            results.setdefault(crit.entry, [])
            results[crit.entry].append(crit.score)

        #sort the dictionary based on sum of the scores array (descending)
        results_order = sorted(results.items(), key=lambda x: sum(x[1]), reverse=True)
        #Create a result record for each item in the sorted array
        for count, result in enumerate(results_order):
            entry = Entry.objects.get(pk = result[0].pk)
            entry.position = count + 1
            entry.score = sum(result[1])
            entry.save()

        #add to the win and lose totals of the respective users.
        #it's a brawl so we only care about top and bottom
        winner = Entry.objects.get(pk = results_order[0][0].pk)
        winner.story.author.brawl_wins += 1
        winner.story.author.save()
        loser = Entry.objects.get(pk = results_order[-1][0].pk)
        loser.story.author.brawl_losses += 1
        loser.story.author.save()
        self.entrant_num = len(results)
        self.status = Contest.CLOSED
        self.save()




class ContestJudges (models.Model):
    """Joining table for contests and judges"""
    contest = models.ForeignKey(Contest,
        on_delete=models.CASCADE,
        related_name = 'contestjudges'
        )
    judge = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name = 'contestjudges')


class Entry(models.Model):
    """Links stories and contests"""
    #because story can be blank initially on signup, we use both story and author, even though author is derivable
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name = 'authors')

    #NB - this is referring to the baseclass Contest, which means there are joins in any query
    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name = 'entries')

    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name = 'entries',
        blank = True)

    position = models.PositiveSmallIntegerField(default=0)
    score = models.PositiveSmallIntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255, blank = True)
    content =  tinymce_models.HTMLField(blank = True)

    class Meta:
        verbose_name_plural = "entries"

    def __str__(self):
        return str(self.story.author) + " : " + self.title

class Crit(models.Model):
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

    entry = models.ForeignKey(
        Entry,
        on_delete=models.SET_NULL,
        null=True,
        related_name = 'crits')
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name = 'crits')
    content = tinymce_models.HTMLField(help_text='Please enter your comments here')
    score = models.IntegerField(choices=SCORE_CHOICES, default=UNSCORED)
    final = models.BooleanField(
        default=False,
        help_text="Check this box if you are finished with your critique. Be warned! - once submitted with this box checked no further edits can be made."
    )
    wordcount = models.PositiveIntegerField(default=100, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.reviewer and self.entry:
            return str(self.entry.contest.title) + " : " + str(self.reviewer.username) + " reviews " + str(self.entry.author.username) # pylint: disable=E1101
        return "ALERT - somehow this crit did not get set a title"
