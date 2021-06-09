"""A series of useful routines for Setting up contests for testing purposes"""
from random import shuffle
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase

from baseapp.models import Story
from promptarena.models import Crit, Entry, Contest
from universal.models import MiniDome

# pylint: disable=attribute-defined-outside-init
# disabled because Django test classes set up variables/attributes in bespoke methods!

class BaseAppTestCase(TestCase):
    """Handy TestClass Extension that can also perform functions to create useful entities"""

    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.user = cls.User.objects.create_user(username='djangotestuser', password='12345abcde')
        cls.user.timezone = "Africa/Abidjan"
        cls.user.save()

    def login_testuser(self, username="djangotestuser"):
        """re-usable code to login class user"""

        self.login = self.client.login(username=username, password='12345abcde')

    def set_up_story_private(self, author = ""):
        """creates private privacy story"""
        if author == "":
            author = self.user
        self.story = Story(title="My Story", content="This is a story all about how...", author = author, access = Story.PRIVATE)
        self.story.save()

    def set_up_story_private_with_wordcount(self,  wordcount = 1001):
        """creates private privacy story with a speciifc wordcount"""
        content = ""
        author = self.user
        for i in range(wordcount):
            content +=  " word" + str(i)
        self.story = Story(title="My Story", content=content, author = author, access = Story.PRIVATE)
        self.story.save()


    def set_up_story_logged_in(self, author = ""):
        """creates logged-in privacy story"""
        if author == "":
            author = self.user
        self.story = Story(title="My Story", content="This is a story all about how...", author = author, access = Story.LOGGED_IN)
        self.story.save()

    def set_up_story_public(self, author = ""):
        """creates public privacy story"""
        if author == "":
            author = self.user
        self.story = Story(title="My Story", content="This is a story all about how...", author = author, access = Story.PUBLIC)
        self.story.save()

    def set_up_multiple_stories(self, num_stories = 100):
        """creates range of  stories and authors and privacy levels
        modulo 3 = public
        3+1 = logged in
        3+2 = private
        """
        self.users = []
        self.stories = []
        for story_num in range(num_stories):
            if story_num % 3 == 0:
                access = Story.PUBLIC
            elif story_num % 3 == 1:
                access = Story.LOGGED_IN
            else:
                access = Story.PRIVATE
            self.users.append(self.User.objects.create_user(username='djangotestuser{}'.format(story_num), password='{}2345abcde'.format(story_num)))
            #users[-1] = last in list
            self.users[-1].save()
            self.stories.append(Story(title="My Story"+str(story_num), content="This is a story all about how...", author = self.users[-1], access = access))
            self.stories[-1].save()

    def set_up_minidome_public(self):
        """creates a minidome public contest
        requires set_up_multiple_stories
        """
        self.minidome = MiniDome(winner = self.stories[0], loser = self.stories[3], minidome_type = MiniDome.PUBLIC)
        self.minidome.save()

    def set_up_minidome_logged_in(self):
        """creates a minidome logged in contest
        requires set_up_multiple_stories
        """
        self.minidome = MiniDome(winner = self.stories[1], loser = self.stories[4], minidome_type = MiniDome.LOGGED_IN)
        self.minidome.save()

    def set_up_contest(self, mode, creator = ""):
        """Re-usable routine to set up contest object"""
        if creator == "":
            creator = self.user
        self.contest = mode(title = "My Contest title",
            start_date = timezone.now(),
            expiry_date = timezone.now() + timezone.timedelta(7),
            status = Contest.OPEN,
            max_wordcount=1000,
            creator=creator
            )

    def set_up_multiple_contests(self, mode, total):
        """Re-usable routine to set up contest object"""
        self.contests = []
        for num in range(total):
            self.contests.append ( mode(
                title = "Contest" + str(num),
                start_date = timezone.now(),
                expiry_date = timezone.now() + timezone.timedelta(7),
                status = Contest.OPEN
                )
            )

    def set_up_contest_components(self, num_entrants = 5):
        """reusable routine to set up contest associated objects
        sets up:
            5 users
            5 stories
            5 entries
        """
        self.users = []
        self.stories = []
        self.entries = []
        for user_num in range(num_entrants):
            self.users.append(self.User.objects.create_user(username='djangotestuser{}'.format(user_num), password='{}2345abcde'.format(user_num)))
            #users[-1] = last in list
            self.users[-1].save()

        for user in self.users:
            self.stories.append(Story(author = user, access=Story.PRIVATE))
            self.stories[-1].save()

        for story in self.stories:
            self.entries.append(Entry(contest = self.contest, story=story))
            self.entries[-1].save()

    def set_up_multiple_contest_components(self):
        """reusable routine to set up contest associated objects
        sets up:
            5 users
            5 stories
            5 entries
        """
        self.users = []
        self.stories = []
        self.entries = []
        for user_num in range(5):
            self.users.append(self.User.objects.create_user(username='djangotestuser{}'.format(user_num), password='{}2345abcde'.format(user_num)))
            #users[-1] = last in list
            self.users[-1].save()

        for user in self.users:
            self.stories.append(Story(author = user, access=Story.PRIVATE))
            self.stories[-1].save()

        for contest in self.contests:
            for story in self.stories:
                self.entries.append(Entry(contest = contest, story=story))
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

    def get_messages(self, response, message_type = ""):
        """todo - figure out of this is needed"""
        type_messages = []
        messages = list(response.context['messages'])
        for message in messages:
            if message_type:
                if message_type in message.tags:
                    type_messages.append(message)
            else:
                type_messages.append(message)
        return type_messages
