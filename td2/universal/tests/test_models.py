"""test universally available functions"""

#from universal.models import MiniDome
from baseapp.tests.test_utils import BaseAppTestCase


class PublicJudgeBattleTest(BaseAppTestCase):
    """Tests the public battle model"""
    def setUpTestData(self):
        self.set_up_multiple_stories_public(num_stories=100)
    def test_minidome_string_representation(self):
        """check model gets saved and has string representation"""
        self.assertEqual(str(self.minidome), self.stories[0].slug + " vs " + self.stories[1].slug)
