"""test universally available functions"""
#from random import sample
#from universal.forms import MiniDomePublicForm
#from universal.models import MiniDome
from baseapp.tests.test_utils import BaseAppTestCase

class PublicJudgeBattleTest(BaseAppTestCase):
    """Tests the public battle model"""
    @classmethod
    def setUpTestData(cls):
        """create a hundred public stories for use"""
        super(PublicJudgeBattleTest, cls).setUpTestData()
        cls.set_up_multiple_stories_public(cls, num_stories=100)

    def test_minidome_string_representation(self):
        """check model gets saved and has string representation"""
        self.set_up_minidome_public()
        self.assertEqual(str(self.minidome), self.stories[0].slug + " vs " + self.stories[1].slug)

    def test_minidome_public_win(self):
        """Make sure stats get updated after win"""
        self.set_up_minidome_public()
        self.assertEqual(self.stories[0].stats.minidome_public_wins, 1)
        self.assertEqual(self.stories[1].stats.minidome_public_losses, 1)
