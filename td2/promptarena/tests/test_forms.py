"""Test framework for users and profiles"""
from django.test import TestCase
from django.utils import timezone
from promptarena.forms import  CreateContestForm, EnterContestNewStoryForm, EnterContestOldStoryForm, ContestStoryForm, EnterCritForm
from promptarena.models import Contest, Crit, InternalJudgeContest
from baseapp.models import Story
from baseapp.utils import HTML_wordcount
from baseapp.tests.test_utils import BaseAppTestCase

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

class EnterContestOldStoryFormTest(TestCase):
    """Enter contest with an old story form test"""
    def setUp(self):
        """set up"""
        self.story = Story(title="Story1", content="This is a <b>story</b>", access=Story.PRIVATE)
        self.story.save()
        self.contest = Contest(max_wordcount = 10, expiry_date = timezone.now() + timezone.timedelta(7), start_date = timezone.now(), title="Contest1", content="This is a <b>contest</b>")
        self.contest.save()
        self.form = EnterContestOldStoryForm(data={"story": self.story},
            story_wordcount = HTML_wordcount(self.story.content),
            contest_max_wordcount = self.contest.max_wordcount,
            contest_expiry_date = self.contest.expiry_date
        )
    def test_enter_contest_old_story_is_valid(self):
        """test form is valid"""
        self.assertTrue(self.form.is_valid())

    def test_enter_contest_old_story_form_exceeds_wordcount(self):
        """test wordcount limit"""
        self.contest.max_wordcount = 1
        self.contest.save()
        self.form = EnterContestOldStoryForm(data={"story":self.story},
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
        self.form = EnterContestOldStoryForm(data={
            "story":self.story},
            story_wordcount = HTML_wordcount(self.story.content),
            contest_max_wordcount = self.contest.max_wordcount,
            contest_expiry_date = self.contest.expiry_date
        )
        self.assertFalse(self.form.is_valid())
        self.assertTrue("The deadline for that contest is over." in self.form.non_field_errors())

class EnterCritFormTest(BaseAppTestCase):
    "Enter a crit for a contest entry"
    def setUp(self):
        self.content = ""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.set_up_contest_components()
        self.contest.close()
        self.dummy_form = EnterCritForm()
        self.score = Crit.HI_SCORE

        for i in range(self.dummy_form.wordcount_min):
            self.content += " word"

        self.form = EnterCritForm( data = {
            "content" : self.content,
            "final" : True,
            "score" : Crit.HI_SCORE
            })

    def test_form_is_valid(self):
        self.assertTrue(self.form.is_valid())

    def test_enter_crit_form_under_wordcount(self):
        self.form = EnterCritForm( data = {
            "content" : "This is a crit",
            "final" : True,
            "score" : self.score,
            },)
        self.assertFalse(self.form.is_valid())
        self.assertTrue("Entrants deserve at least " + str(self.form.wordcount_min) + " words for their efforts!"  in self.form.non_field_errors())

    def test_enter_crit_form_no_score(self):
        self.form = EnterCritForm( data = {
            "content" : self.content,
            "final" : True,
            "score" : Crit.UNSCORED,
            },)
        self.assertFalse(self.form.is_valid())
        self.assertTrue("You can't submit a final judgement without a score."  in self.form.non_field_errors())






