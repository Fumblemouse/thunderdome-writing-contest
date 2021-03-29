"""Tests to run entire contests from beginning to end """
from promptarena.models import Prompt,  InternalJudgeContest, Entry, Crit
from baseapp.models import Story
from baseapp.tests.test_utils import BaseAppTestCase

class ContestTest(BaseAppTestCase):
    """tests various contest types form beginning to end'"""
    #@classmethod
    #def setUpTestData(cls):
    #    super(ContestTest, cls).setUpTestData()
    def test_internal_judge_contest(self):
        """creates and scores internal judge contest"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.set_up_contest_components()
        self.score_contest()
