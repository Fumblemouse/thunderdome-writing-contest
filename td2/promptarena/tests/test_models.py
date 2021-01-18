"""Test models for Stories"""
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from promptarena.models import Prompt, Contest, Entry, Crit
from baseapp.models import Story


class PromptModelTest(TestCase):

    """Test A Prompt"""
    def setUp(self):
        self.prompt = Prompt(title="My Prompt title")
    def test_prompt_string_representation(self):
        self.assertEqual(str(self.prompt), self.prompt.title)
    #def test_prompt_verbose_name_plural(self):
    #    self.assertEqual(str(Prompt._meta.verbose_name_plural), "stories")
    def test_prompt_save_function(self):
        self.prompt.save()
        self.assertTrue(self.prompt.slug == "my-prompt-title")
    def test_prompt_save_title_again_function(self):
        self.prompt.public_view_allowed = False
        self.prompt.title = "my changed title"
        self.prompt.save()
        self.assertTrue(self.prompt.slug == "my-changed-title")

class ContestModelTest(TestCase):

    """Test A Prompt"""
    def setUp(self):
        self.prompt = Prompt(title="My Prompt title")
        self.prompt.save()
        self.contest = Contest(prompt=self.prompt, start_date = timezone.now(), expiry_date = timezone.now() + timezone.timedelta(7))
        user = get_user_model()
        self.user1 = user.objects.create_user(username='djangotestuser1', password='12345')
        self.user2 = user.objects.create_user(username='djangotestuser2', password='12346')
        self.user3 = user.objects.create_user(username='djangotestuser3', password='12347')
        self.user4 = user.objects.create_user(username='djangotestuser4', password='12348')
        self.user5 = user.objects.create_user(username='djangotestuser5', password='12349')
        self.story1 = Story(author = self.user1)
        self.story2 = Story(author = self.user2)
        self.story3 = Story(author = self.user3)
        self.story4 = Story(author = self.user4)
        self.story5 = Story(author = self.user5)
        self.entry1 = Entry(contest = self.contest, story=self.story1)
        self.entry2 = Entry(contest = self.contest, story=self.story2)
        self.entry3 = Entry(contest = self.contest, story=self.story3)
        self.entry4 = Entry(contest = self.contest, story=self.story4)
        self.entry5 = Entry(contest = self.contest, story=self.story5)



    def test_contest_string_representation(self):
        self.assertEqual(str(self.contest), self.contest.prompt.title)
    def test_contest_save_function(self):
        self.contest.save()
        self.assertTrue(self.contest.slug == "my-prompt-title")
    def test_contest_save_title_again_function(self):
        self.contest.prompt.title = "my changed title"
        self.contest.prompt.save()
        self.contest.save()
        self.assertTrue(self.contest.slug == "my-changed-title")
    def test_contest_open_function(self):
        self.contest.open()
        self.assertTrue(self.contest.status == "OPEN")
    def test_contest_close_function(self):
        self.contest.close()
        self.assertEqual(self.contest.status,'JUDGEMENT')
    def test_contest_close_crit_creation_test(self):
        self.contest.close()
        self.assertEqual(Crit.objects.all().count(), 15)
    def test_contest_close_crit_creation(self):
        self.contest.close()
        self.assertEqual(Crit.objects.filter(entry__contest = self.contest).count(), 15)
