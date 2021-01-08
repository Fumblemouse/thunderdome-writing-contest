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
from baseapp.models import Story
from baseapp.utils import sattolo_cycle


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
    slug = AutoSlugField(max_length=200, unique=True)

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
    UNOPENED = 'UNOPENED'
    OPEN='OPEN'
    JUDGEMENT = 'JUDGEMENT'
    CLOSED = 'CLOSED'
    CONTEST_STATES = [
        (UNOPENED, 'Unopened'),
        (OPEN, 'Open'),
        (JUDGEMENT, 'Judgement'),
        (CLOSED, 'Closed')
    ]
    prompt = models.ForeignKey(Prompt, on_delete=models.SET_NULL, null=True) #Null = true to make on_delete work
    start_date = models.DateTimeField('Start Date')
    expiry_date = models.DateTimeField('Submit by Date')
    status= models.CharField(choices=CONTEST_STATES, default='Unopened', max_length=9)
    wordcount = models.PositiveIntegerField(default=1000)
    slug = AutoSlugField(max_length=200, default='no-contest-slug', unique=True)

    def __str__(self):
        if self.prompt:
            return self.prompt.title
        return "ALERT - somehow this contest did not get set a title"

    def is_active(self):
        '''returns true if expiry date is passed'''
        return self.expiry_date > timezone.now() > self.start_date

    #def save(self, *args, **kwargs):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        slug = self.slug
        if not self.id or slug.startswith('no-contest-') or slug=='':
            self.slug = "contest-" + slugify(self.prompt.title)
        super(Contest, self).save()

    def close(self):
        """assign stories to judges"""
        #get list of entries to this contest
        entries = Entry.objects.filter(contest = self)
        #get list of entrants and stories from entries
        stories = entries.values_list('story', flat=True)
        stories = list(stories)
        entrants = entries.values_list('story__author', flat=True)
        entrants = list(entrants)

        #setup container for creating crit requirements, fill it with [entrant [list,of,stories]]
        judges_with_stories = list()

        for entrant in entrants:
            judges_with_stories.append([entrant, []])
        loopmax = 3

        loop =1
        #breakpoint()
        while loop <= loopmax:
            shuffled_stories = sattolo_cycle(stories.copy())
            judge_temp = self.assign_stories(shuffled_stories, judges_with_stories)
            if judge_temp == "error":
                print(judges_with_stories)
            else:
                judges_with_stories = judge_temp
                loop += 1

        for judge in judges_with_stories:
            reviewer =  get_user_model().objects.get(pk = judge[0])
            for story in judge[1]:
                story_instance = Story.objects.get(pk = story)
                contest_instance = self
                entry = Entry.objects.get(contest = contest_instance, story=story_instance)
                Crit.objects.create(story = story_instance, reviewer= reviewer, entry = entry )
        self.status = 'JUDGEMENT'
        self.save()

    def assign_stories(self, shuffled_stories, judges_with_stories):
        """checks for duplicates and returns list if there are none"""
	    #test for pre-existing things
        for judge in enumerate(judges_with_stories):
            if shuffled_stories[judge[0]] in judges_with_stories[judge[0]][1]:
                return "error"
        #nothing pre-existing - merge the array
        for story in enumerate(judges_with_stories):
            judges_with_stories[story[0]][1].append(shuffled_stories[story[0]])
        return judges_with_stories

    def judge(self):
        """Count, Sort the results and"""
        crits = Crit.objects.filter(contest = self.pk)
        results = {}
        results_order = {}
        #create a dictionary with story as key and an array of two arrays scores, and
        for crit in crits:
            results.setdefault(crit.story, [[],crit.story.author])
            results[crit.story][0].append(crit.score)
            #results[crit.story][1] = crit.story.author

        #sort the dictionary based on sum of the array (descending)
        results_order = sorted(results.items(), key=lambda x: sum(x[1][0]), reverse=True)
        #Create a result record for each item in the sorted array
        for count, result in enumerate(results_order):
            resultRow = Result.objects.create_result(self, result[1][1], result[0], len(results), count + 1, sum(result[1][0]))
            resultRow.save()
        self.status = 'CLOSED'
        self.save()


class ResultManager(models.Manager):
    """Manager class so that they can be created by other models"""
    def create_result(self, contest, entrant, story, number_of_entrants, position, score):
        result = self.create(contest = contest, entrant = entrant, story = story, number_of_entrants = number_of_entrants, position = position, score = score)
        # do something with the Result
        return result

class Result(models.Model):
    """Stores results of contests, including positions, entrants and number of other entrants"""
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    entrant =  models.ForeignKey(
      get_user_model(),
      on_delete=models.SET_NULL,
      null=True
    )
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    number_of_entrants = models.PositiveSmallIntegerField()
    position = models.PositiveSmallIntegerField()
    score = models.PositiveSmallIntegerField()

    objects = ResultManager()

    def __str__(self):
        if self.contest:
            return str(self.contest.prompt.title) + " : " + str(self.entrant.username)
        return "ALERT - somehow this result did not get set a title"



class Entry(models.Model):
    """Links stories and contests"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    contest_scores = models.CharField(blank=True, max_length=200)

    def __str__(self):
        if self.story and self.contest:
            return str(self.story.author) + " : " + self.contest.prompt.title
        return "ALERT - somehow this entry did not get set a title"

    class Meta:
        verbose_name_plural = "entries"


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
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.SET_NULL, null=True)
    reviewer = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    content = tinymce_models.HTMLField(help_text='Please enter your comments here')
    score = models.IntegerField(choices=SCORE_CHOICES, default=UNSCORED)
    final = models.BooleanField(blank = True, default=False)
    wordcount = models.PositiveIntegerField(default=1000, null=True)

    def __str__(self):
        if self.reviewer and self.entry:
            return str(self.entry.contest.prompt.title) + " : " + str(self.reviewer.username) + " reviews " + str(self.story.author) # pylint: disable=E1101
        return "ALERT - somehow this crit did not get set a title"
