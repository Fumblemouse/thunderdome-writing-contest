"""Test framework for users and profiles"""
from django.test import TestCase
from django.urls import reverse
# Create your tests here.
from django.contrib.auth import get_user_model

from baseapp.models import Story
from promptarena.models import Prompt, Contest, Entry, Crit, InternalJudgeContest
from baseapp.tests.test_utils import BaseAppTestCase
# Create your tests here.

class PromptArenaViewTest(BaseAppTestCase):
    """test views are available (login happens where needed)"""
    @classmethod
    def setUpTestData(cls):
        cls.user = cls.create_testuser(cls)
        cls.user.save()
        #cls.story = cls.set_up_story_private(cls)

    def test_view_prompts_view_exists(self):
        self.set_up_prompt()
        response = self.client.get(reverse('view prompts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/view-prompts.html')

    def test_view_contests_view_exists(self):
        self.set_up_contest(InternalJudgeContest)
        response = self.client.get(reverse('view contests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/view-contests.html')

    def test_view_prompt_details_view_exists(self):
        self.set_up_prompt()
        response = self.client.get(reverse('view prompt details', kwargs = {'prompt_id': self.prompt.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/view-prompt-details.html')

    def test_view_contest_details_view_exists(self):
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        response = self.client.get(reverse('view contest details', kwargs = {'contest_id': self.contest.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/view-contest-details.html')

    def test_create_prompt_view_exists(self):
        self.login_testuser('djangotestuser')
        response = self.client.get(reverse('create prompt'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/create-prompt.html')

    def test_edit_prompt_view_exists(self):
        self.login_testuser('djangotestuser')
        self.set_up_prompt()
        response = self.client.get(reverse('edit prompt',  kwargs = {"prompt_id": self.prompt.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/create-prompt.html')

    def test_create_contest_new_prompt_view_exists(self):
        self.login_testuser('djangotestuser')
        self.set_up_prompt()
        response = self.client.get(reverse('create contest'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/create-contest-new-prompt.html')

    def test_create_contest_old_prompt_view_exists(self):
        self.login_testuser('djangotestuser')
        self.set_up_prompt()
        response = self.client.get(reverse('create contest old prompt'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/create-contest-old-prompt.html')

    def test_enter_contest_new_story_view_exists(self):
        self.login_testuser('djangotestuser')
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        response = self.client.get(reverse('enter contest', kwargs = {"contest_id": self.contest.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/enter-contest-new-story.html')

    def test_enter_contest_old_story_view_exists(self):
        self.login_testuser('djangotestuser')
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        response = self.client.get(reverse('enter contest old story',  kwargs = {"contest_id": self.contest.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/enter-contest-old-story.html')

    def test_judgemode_view_exists(self):
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.set_up_contest_components()
        self.login_testuser('djangotestuser1')
        response = self.client.get(reverse('judgemode'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/judgemode.html')

    def test_judgemode_crit_view_exists(self):
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.set_up_contest_components()
        self.contest.close()
        self.login_testuser('djangotestuser1')
        crits = Crit.objects.filter(reviewer = self.user)
        for crit in crits:
            response = self.client.get(reverse('judgemode', kwargs = {'crit_id': crit.pk}))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'promptarena/judgemode.html')

class PromptArenaLoginAccessTest(BaseAppTestCase):
    """test login required to access pages"""
    def test_create_prompt_view_restricted(self):
        response = self.client.get(reverse('create prompt'))
        self.assertRedirects(response, '/accounts/login/?next=/create-prompt')

    def test_edit_prompt_view_restricted(self):
        self.set_up_prompt()
        response = self.client.get(reverse('edit prompt', kwargs = {"prompt_id": self.prompt.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/1/edit-prompt')

    def test_create_contest_view_restricted(self):
        response = self.client.get(reverse('create contest'))
        self.assertRedirects(response, '/accounts/login/?next=/create-contest')

    def test_create_contest_old_prompt_view_restricted(self):
        response = self.client.get(reverse('create contest old prompt'))
        self.assertRedirects(response, '/accounts/login/?next=/create-contest-old-prompt')

    def test_enter_contest_view_restricted(self):
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        response = self.client.get(reverse('enter contest', kwargs = {"contest_id": self.contest.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/1/enter-contest')

    def test_enter_contest_old_prompt_view_restricted(self):
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        response = self.client.get(reverse('enter contest old story', kwargs = {"contest_id": self.contest.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/1/enter-contest-old-story')

    def test_judgemode_view_restricted(self):
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.set_up_contest_components()
        self.contest.close()
        response = self.client.get(reverse('judgemode'))
        self.assertRedirects(response, '/accounts/login/?next=/judgemode')

    def test_judgemode_crit_view_restricted(self):
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.set_up_contest_components()
        self.contest.close()
        response = self.client.get(reverse('judgemode', kwargs = {'crit_id': 1}))
        self.assertRedirects(response, '/accounts/login/?next=/1/judgemode')
