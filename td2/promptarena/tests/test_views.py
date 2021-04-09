"""Test framework for users and profiles"""
from django.urls import reverse
# Create your tests here.

from promptarena.models import InternalJudgeContest, Crit
from baseapp.tests.test_utils import BaseAppTestCase
# Create your tests here.

class PromptArenaViewTest(BaseAppTestCase):
    """test views are available (login happens where needed)"""
    @classmethod
    def setUpTestData(cls):
        #Call the super to get user created
        super(PromptArenaViewTest, cls).setUpTestData()
        cls.set_up_story_private(cls)


    def test_view_contests_view_exists(self):
        """test view contests view exists"""
        self.set_up_contest(InternalJudgeContest)
        response = self.client.get(reverse('view contests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/view-contests.html')

    def test_view_contest_details_view_exists(self):
        """test view contest details view exists"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        response = self.client.get(reverse('view contest details', kwargs = {'contest_id': self.contest.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/view-contest-details.html')


    def test_create_contest_view_exists(self):
        """test create contest with a new prompt view exists"""
        self.login_testuser('djangotestuser')
        response = self.client.get(reverse('create contest'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/create-contest.html')

    def test_enter_contest_new_story_view_exists(self):
        """test enter contest with new story view exists"""
        self.login_testuser('djangotestuser')
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        response = self.client.get(reverse('enter contest', kwargs = {"contest_id": self.contest.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/enter-contest-new-story.html')

    def test_enter_contest_old_story_view_exists(self):
        """test enter contest with an old story view exists"""
        self.login_testuser('djangotestuser')
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        response = self.client.get(reverse('enter contest old story',  kwargs = {"contest_id": self.contest.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/enter-contest-old-story.html')

    def test_judgemode_view_exists(self):
        """test judgemode view exists"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.set_up_contest_components()
        self.login_testuser('djangotestuser1')
        response = self.client.get(reverse('judgemode'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/judgemode.html')

    def test_judgemode_crit_view_exists(self):
        """test judgemode crit view exists"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.set_up_contest_components()
        self.contest.close()
        self.login_testuser('djangotestuser1')
        crits = Crit.objects.filter(reviewer__username = 'djangotestuser1')
        for crit in crits:
            response = self.client.get(reverse('judgemode', kwargs = {'crit_id': crit.pk}))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'promptarena/judgemode.html')

class PromptArenaLoginAccessTest(BaseAppTestCase):
    """Test login required working for where it is needed in promprtarena app"""


    def test_create_contest_view_restricted(self):
        """test login required to access create contest"""
        response = self.client.get(reverse('create contest'))
        self.assertRedirects(response, '/accounts/login/?next=/create-contest')

    def test_enter_contest_view_restricted(self):
        """test login required to access enter contest"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        response = self.client.get(reverse('enter contest', kwargs = {"contest_id": self.contest.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/1/enter-contest')

    def test_enter_contest_old_story_view_restricted(self):
        """test login required to access enter contest with old story """
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        response = self.client.get(reverse('enter contest old story', kwargs = {"contest_id": self.contest.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/1/enter-contest-old-story')

    def test_judgemode_view_restricted(self):
        """test login required to access judgemode"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.set_up_contest_components()
        self.contest.close()
        response = self.client.get(reverse('judgemode'))
        self.assertRedirects(response, '/accounts/login/?next=/judgemode')

    def test_judgemode_crit_view_restricted(self):
        """test login required to access judegmode crit view"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.set_up_contest_components()
        self.contest.close()
        response = self.client.get(reverse('judgemode', kwargs = {'crit_id': 1}))
        self.assertRedirects(response, '/accounts/login/?next=/1/judgemode')
