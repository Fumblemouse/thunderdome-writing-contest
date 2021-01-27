"""A series of useful routines for Setting up contests for testing purposes"""
from random import shuffle
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase

from baseapp.models import Story
from promptarena.models import Prompt, Entry, Crit

class BaseAppTestCase(TestCase):
    """Handy TestClass Extension that can also perform functions to create useful entities"""


    def __init__(self, *args, **kwargs):
        """Class with routines for testing contest as doing little jobs"""
        super(BaseAppTestCase, self).__init__(*args, **kwargs)

        #self.login=None
        #self.story = None
        #self.prompt = None
        #self.contest = None
        #self.users = None
        #self.stories = None
        #self.entries = None
        #self.crits = None

    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.user = cls.User.objects.create_user(username='djangotestuser', password='12345abcde')
        cls.user.profile.timezone = "Africa/Abidjan"
        cls.user.save()


    def get_testuser(self):
        """create default user"""
        #User = get_user_model()
        #self.user = User.objects.create_user(username='djangotestuser', password='12345abcde')
        return self.user

    def login_testuser(self, username):
        """re-usable code to login class user"""
        self.login = self.client.login(username=username, password='12345abcde')

    def set_up_story_private(self, author = ""):
        """creates private story"""
        if author == "":
            author = self.user
        self.story = Story(title="My Story", content="This is a story all about how...", author = author, public = False)
        self.story.save()

    def set_up_story_public(self, author = ""):
        """creates private story"""
        if author == "":
            author = self.user
        self.story = Story(title="My Story", content="This is a story all about how...", author = author, public = True)
        self.story.save()

    def set_up_prompt(self):
        """Creates a prompt"""
        self.prompt = Prompt(title="My Prompt title")
        self.prompt.save()

    def set_up_contest(self, mode):
        """Re-usable routine to set up contest object"""
        self.set_up_prompt()
        self.contest = mode(prompt=self.prompt,
            start_date = timezone.now(),
            expiry_date = timezone.now() + timezone.timedelta(7),
            status = 'OPEN'
            )

    def set_up_contest_components(self):
        """reusable routine to set up contest associated objects"""
        self.users = []
        self.stories = []
        self.entries = []
        for user_num in range(5):
            self.users.append(self.User.objects.create_user(username='djangotestuser{}'.format(user_num), password='{}2345abcde'.format(user_num)))
            #users[-1] = last in list
            self.users[-1].save()
        for user in self.users:
            self.stories.append(Story(author = user, public=False))
            self.stories[-1].save()
        for story in self.stories:
            self.entries.append(Entry(contest = self.contest, story=story))
            self.entries[-1].save()


    def score_contest(self):
        """reuable routine to assign scores to contest entries"""
        for user in self.users:
            scores = [3,5,7,11,13]
            self.crits = Crit.objects.filter(entry__contest = self.contest, reviewer = user)
            for crit in self.crits:
                shuffle(scores)
                crit.score = scores.pop()
                crit.save()
