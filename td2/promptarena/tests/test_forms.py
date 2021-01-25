"""Test framework for users and profiles"""
from django.test import TestCase
# Create your tests here.
from django.contrib.auth import get_user_model
from django.utils import timezone
from promptarena.forms import PromptForm, CreateContestNewPromptForm, CreateContestOldPromptForm, EnterContestNewStoryForm
from promptarena.models import Prompt, Contest
from baseapp.models import Story
from baseapp.utils import HTML_wordcount

class PromptFormTest(TestCase):
    """Prompt form test"""
    def setUp(self):
        """Set up"""
        self.form = PromptForm(data={"title": "prompt title", "content": "This is a <b>prompt<b>"})
    def test_prompt_form_valid(self):
        """test form is valid"""
        self.assertTrue(self.form.is_valid)

class CreateContestNewPromptFormtTest(TestCase):
    """Create a contest with a new prompt form test"""
    def setUp(self):
        """set up"""
        self.form = CreateContestNewPromptForm(data={"max_wordcount": 10, "expiry_date": timezone.now() + timezone.timedelta(7), "start_date": timezone.now()})
    def test_create_contest_new_prompt_form_valid(self):
        """validate the form"""
        self.assertTrue(self.form.is_valid)

class CreateContestOldPromptFormTest(TestCase):
    """Create contest with an old prompt form test"""
    def setUp(self):
        """set up"""
        self.prompt = Prompt(title = "Prompt1", content="this is a <b>prompt</b>")
        self.form = CreateContestOldPromptForm(data={
            "prompt": self.prompt,
            "max_wordcount": 10,
            "expiry_date": timezone.now() + timezone.timedelta(7),
            "start_date": timezone.now()
        })
    def test_create_contest_old_prompt_form_valid(self):
        """validate the form"""
        self.assertTrue(self.form.is_valid)

class EnterContestNewStoryFormTest(TestCase):
    """Enter contest with a new story form test"""
    def setUp(self):
        """set up"""
        self.prompt = Prompt(title = "Prompt1", content="this is a <b>prompt</b>")
        self.prompt.save()
        self.story = Story(title="Story1", content="this is content", public=False)
        self.story.save()
        self.contest = Contest(max_wordcount = 10, expiry_date = timezone.now() + timezone.timedelta(7), start_date = timezone.now(), prompt=self.prompt)
        self.contest.save()
        self.form = EnterContestNewStoryForm(data={},
            story_wordcount = HTML_wordcount(self.story.content),
            contest_max_wordcount = self.contest.max_wordcount,
            contest_expiry_date = self.contest.expiry_date
        )
    def test_enter_contest_new_story_is_valid(self):
        """test form is valid"""
        self.assertTrue(self.form.is_valid())

    def test_enter_contest_new_story_form_exceeds_wordcount(self):
        """test wordcount limit"""
        self.contest.max_wordcount = 1
        self.contest.save()
        self.form = EnterContestNewStoryForm(data={},
            story_wordcount = HTML_wordcount(self.story.content),
            contest_max_wordcount = self.contest.max_wordcount,
            contest_expiry_date = self.contest.expiry_date
        )
        self.assertFalse(self.form.is_valid())
        self.assertTrue("More words than wordcount. Kill your darlings!" in self.form.non_field_errors())

    def test_enter_contest_form_contest_expired(self):
        """test expiry date not passed"""
        self.contest.expiry_date = timezone.now() - timezone.timedelta(7)
        self.contest.save()
        self.form = EnterContestNewStoryForm(data={},
            story_wordcount = HTML_wordcount(self.story.content),
            contest_max_wordcount = self.contest.max_wordcount,
            contest_expiry_date = self.contest.expiry_date
        )
        self.assertFalse(self.form.is_valid())
        self.assertTrue("The deadline for that contest is over." in self.form.non_field_errors())


