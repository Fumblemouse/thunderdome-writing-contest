"""test universally available functions"""
# from random import sample
# from universal.forms import MiniDomePublicForm
# from universal.models import MiniDome
from baseapp.models import Story
from baseapp.tests.test_utils import BaseAppTestCase


class PublicJudgeBattleTest(BaseAppTestCase):
    """Tests the public battle model"""

    @classmethod
    def setUpTestData(cls):
        """create a hundred public stories for use"""
        super(PublicJudgeBattleTest, cls).setUpTestData()
        cls.set_up_multiple_stories(cls, num_stories=100)

    def test_minidome_string_representation(self):
        """check model gets saved and has string representation"""
        self.set_up_minidome_public()
        self.assertEqual(
            str(self.minidome), self.stories[0].slug + " vs " + self.stories[3].slug
        )

    def test_minidome_public_stats(self):
        """Make sure public stats get updated after win
        then add another win and make sure they are added again"""
        self.set_up_minidome_public()
        self.assertEqual(self.stories[0].access, Story.PUBLIC)
        self.assertEqual(self.stories[3].access, Story.PUBLIC)
        self.assert_minidome_public_stats(1)
        self.set_up_minidome_public()
        self.assert_minidome_public_stats(2)

    def assert_minidome_public_stats(self, score):
        self.assertEqual(self.stories[0].stats.minidome_public_wins, score)
        self.assertEqual(self.stories[0].stats.minidome_public_losses, 0)
        self.assertEqual(self.stories[3].stats.minidome_public_wins, 0)
        self.assertEqual(self.stories[3].stats.minidome_public_losses, score)
        self.assertEqual(self.stories[3].stats.get_minidome_total_public_tests(), score)

    def test_minidome_logged_in_stats(self):
        """Make sure logged in stats get updated after win"""
        self.set_up_minidome_logged_in()
        self.assertEqual(self.stories[1].access, Story.LOGGED_IN)
        self.assertEqual(self.stories[4].access, Story.LOGGED_IN)
        self.assert_minidome_logged_in_stats(1)
        self.set_up_minidome_logged_in()
        self.assert_minidome_logged_in_stats(2)

    def assert_minidome_logged_in_stats(self, score):
        self.assertEqual(self.stories[1].stats.minidome_logged_in_wins, score)
        self.assertEqual(self.stories[1].stats.minidome_logged_in_losses, 0)
        self.assertEqual(self.stories[4].stats.minidome_logged_in_wins, 0)
        self.assertEqual(self.stories[4].stats.minidome_logged_in_losses, score)
        self.assertEqual(
            self.stories[1].stats.get_minidome_total_logged_in_tests(), score
        )
