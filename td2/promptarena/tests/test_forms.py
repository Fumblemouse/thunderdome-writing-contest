"""Test framework for users and profiles"""
from django.test import TestCase
from django.utils import timezone
from promptarena.forms import  CreateContestForm, EnterContestNewStoryForm, ContestStoryForm
from promptarena.models import Contest
from baseapp.models import Story
from baseapp.utils import HTML_wordcount

# Create your tests here.

class ContestStoryFormTest(TestCase):
    """Story in a contest form test"""
    def setUp(self):
        """Set up"""
        self.form = ContestStoryForm(data={"title": "Story title", "content": "This is a <b>story<b>"})
    def test_contest_story_form_valid(self):
        """test form is valid"""
        self.assertTrue(self.form.is_valid)

class CreateContestFormtTest(TestCase):
    """Create a contest with a new contest form test"""
    def setUp(self):
        """set up"""
        self.form = CreateContestForm(data={"Title": "Contest Title", "Content": "This is a <b>contest<b>", "max_wordcount": 10, "expiry_date": timezone.now() + timezone.timedelta(7), "start_date": timezone.now()})
    def test_create_contest_form_valid(self):
        """validate the form"""
        self.assertTrue(self.form.is_valid)


class EnterContestNewStoryFormTest(TestCase):
    """Enter contest with a new story form test"""
    def setUp(self):
        """set up"""
        self.story = Story(title="Story1", content="This is a <b>story</b>", access=Story.PRIVATE)
        self.story.save()
        self.contest = Contest(max_wordcount = 10, expiry_date = timezone.now() + timezone.timedelta(7), start_date = timezone.now(), title="Contest1", content="This is a <b>contest</b>")
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
