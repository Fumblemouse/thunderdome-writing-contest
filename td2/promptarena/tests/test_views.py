"""Test framework for views in promptarena"""
from django.urls import reverse
from django.utils import timezone
# Create your tests here.

from promptarena.models import InternalJudgeContest, ExternalJudgeContest,Crit, Contest
from promptarena.forms import  EnterCritForm
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

    def test_add_judge_view_exists(self):
        """Test add a judge view exists"""
        self.login_testuser('djangotestuser')
        self.set_up_contest(ExternalJudgeContest)
        self.contest.save()
        response = self.client.get(reverse('add judge', kwargs = { 'contest_id' : self.contest.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promptarena/add-judge.html')


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

    def test_add_judge_restricted(self):
        """test login required to access add judge view"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        response = self.client.get(reverse('add judge', kwargs = {'contest_id': self.contest.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/1/add-judge')

class PromptArenaViewsWithData(BaseAppTestCase):
    """Test what happens when things get real - with real data"""
    def setUp(self):
        self.login_testuser('djangotestuser')

    def test_create_contest(self):
        """Post creater contest form and see if it goes through"""
        response = self.client.post(reverse('create contest'), {
            'title' : 'My Contest title',
            'content' : 'My Contest content',
            'start_date' :timezone.now(),
            'expiry_date' : timezone.now() + timezone.timedelta(7),
            'max_wordcount' : 1000,
        })
        self.assertRedirects(response, '/view-contests')

    def test_edit_contest_not_creator(self):
        """Access edit contest form if you are not creator of contest"""
        self.notcreator = self.User.objects.create_user(username='notcreator', password='12345abcde')
        self.notcreator.save()
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.login_testuser('notcreator')
        response = self.client.post(reverse('edit contest', kwargs = {'contest_id' : self.contest.pk}), {
            'title' : 'My Contest title',
            'content' : 'My Contest content',
            'start_date' :timezone.now(),
            'expiry_date' : timezone.now() + timezone.timedelta(7),
            'max_wordcount' : 1000,
        })
        self.assertRedirects(response, '/view-contests')


    def test_edit_contest_live_creator_access(self):
        """access edit contest form if you are creator"""
        self.client.post(reverse('create contest'), {
            'title' : 'My Contest title',
            'content' : 'My Contest content',
            'start_date' :timezone.now(),
            'expiry_date' : timezone.now() + timezone.timedelta(7),
            'max_wordcount' : 1000,
        })

        self.contest = Contest.objects.get(creator__username = 'djangotestuser')

        response = self.client.post(reverse('edit contest', kwargs = {'contest_id' : self.contest.pk}), {
            'title' : 'My Contest title',
            'content' : 'My Contest content',
            'start_date' :timezone.now(),
            'expiry_date' : timezone.now() + timezone.timedelta(7),
            'max_wordcount' : 1000,
        })
        self.assertRedirects(response, "/" + str(self.contest.pk) + '/view-contest-details')


    def test_edit_contest_unopened_creator_access(self):
        """access edit contest form if you are creator"""
        self.login_testuser('djangotestuser')
        self.client.post(reverse('create contest'), {
            'title' : 'My Contest title',
            'content' : 'My Contest content',
            'start_date' :timezone.now()  + timezone.timedelta(1),
            'expiry_date' : timezone.now() + timezone.timedelta(7),
            'max_wordcount' : 1000,
        })

        self.contest = Contest.objects.get(creator__username = 'djangotestuser')

        response = self.client.post(reverse('edit contest', kwargs = {'contest_id' : self.contest.pk}), {
            'title' : 'My Contest title',
            'content' : 'My Contest content revised',
            'start_date' :timezone.now() + timezone.timedelta(1),
            'expiry_date' : timezone.now() + timezone.timedelta(7),
            'max_wordcount' : 1000,
        })
        self.assertRedirects(response, '/view-contests')

    def test_edit_contest_invalid_form(self):
        """Test how form proceeds if invalid"""
        self.client.post(reverse('create contest'), {
            'title' : 'My Contest title',
            'content' : 'My Contest content',
            'start_date' :timezone.now()  + timezone.timedelta(1),
            'expiry_date' : timezone.now() + timezone.timedelta(7),
            'max_wordcount' : 1000,
        })

        self.contest = Contest.objects.get(creator__username = 'djangotestuser')

        response = self.client.post(reverse('edit contest', kwargs = {'contest_id' : self.contest.pk}), {
            'title' : 'My big fat failed form',
            'content' : 'My Contest content revised',
            'start_date' :timezone.now() + timezone.timedelta(1),
            'expiry_date' : timezone.now() + timezone.timedelta(7),
        #removing commented line  fails valdiations
        #    'max_wordcount' : 1000,
        })
        self.assertTemplateUsed(response, 'promptarena/create-contest.html')

    def test_enter_contest_new_story(self):
        """Post a new story to a contest"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        response = self.client.post(reverse('enter contest', kwargs = {'contest_id' : self.contest.pk}), {
            'title' : 'My Story title',
            'content' : 'My Story content',
        })
        self.assertRedirects(response, '/view-contests')

    def test_enter_contest_new_story_invalid_story(self):
        """Post a new story to a contest"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        response = self.client.post(reverse('enter contest', kwargs = {'contest_id' : self.contest.pk}), {
            'content' : 'My Story content',
        })
        self.assertTemplateUsed(response, 'promptarena/enter-contest-new-story.html')

    def test_enter_contest_new_story_invalid_entry(self):
        """Post a new story to a contest"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        story_content = ""
        for i in range(1010):
            story_content += " word"
        response = self.client.post(reverse('enter contest', kwargs = {'contest_id' : self.contest.pk}), {
            'title' : "My story title",
            'content' : story_content,
        })
        self.assertTemplateUsed(response, 'promptarena/enter-contest-new-story.html')

    def test_enter_contest_new_story_not_open(self):
        """Post a new story to a contest"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.status = Contest.JUDGEMENT
        self.contest.save()
        response = self.client.post(reverse('enter contest', kwargs = {'contest_id' : self.contest.pk}), {
            'title' : 'My Story title',
            'content' : 'My Story content  ',
        })
        self.assertTemplateUsed(response, 'promptarena/enter-contest-new-story.html')

    def test_enter_contest_old_story(self):
        """Post an old story to a contest"""
        self.set_up_story_private()
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        response = self.client.post(reverse('enter contest old story', kwargs = {'contest_id' : self.contest.pk}), {
            'story' : self.story.pk
        })
        self.assertRedirects(response, '/view-contests')


    def test_enter_contest_old_story_invalid_entry(self):
        """Post a new story to a contest"""
        self.set_up_story_private_with_wordcount(wordcount = 1001)
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        response = self.client.post(reverse('enter contest old story', kwargs = {'contest_id' : self.contest.pk}), {
            'story' : self.story.pk
        })
        self.assertTemplateUsed(response, 'promptarena/enter-contest-old-story.html')

    def test_enter_contest_old_story_not_open(self):
        """Post an old story to a contest"""
        self.set_up_story_private()
        self.set_up_contest(InternalJudgeContest)
        self.contest.status = Contest.JUDGEMENT
        self.contest.save()
        response = self.client.post(reverse('enter contest old story', kwargs = {'contest_id' : self.contest.pk}), {
            'story' : self.story.pk
        })
        self.assertRedirects(response, '/view-contests')

    def test_add_judge_add_judge_by_creator(self):
        """Add a single judge to a contest (default functionality)"""
        self.set_up_contest(ExternalJudgeContest)
        self.contest.save()
        response = self.client.post(reverse('add judge', kwargs = {'contest_id' : self.contest.pk}), {
            'judge' : self.user.pk
        })

        self.assertTemplateUsed(response, 'promptarena/add-judge.html')

    def test_add_judge_add_judge_by_notcreator(self):
        """Add a judge when you are not the contest creator"""
        self.set_up_contest(ExternalJudgeContest)
        self.notcreator = self.User.objects.create_user(username='notcreator', password='12345abcde')
        self.notcreator.save()
        self.contest.save()
        self.login_testuser('notcreator')
        response = self.client.post(reverse('add judge', kwargs = {'contest_id' : self.contest.pk}), {
            'judge' : self.user.pk
        })

        self.assertRedirects(response, '/view-contests')

    def test_add_judge_add_same_judge(self):
        """Add a single judge TWICE to a contest
        NB - we do this via view rather than form """
        self.set_up_contest(ExternalJudgeContest)
        self.notcreator = self.User.objects.create_user(username='notcreator', password='12345abcde')
        self.notcreator.save()
        self.contest.save()
        response = self.client.post(reverse('add judge', kwargs = {'contest_id' : self.contest.pk}), {
            'judge' : self.notcreator.pk
        })
        response = self.client.post(reverse('add judge', kwargs = {'contest_id' : self.contest.pk}), {
            'judge' : self.notcreator.pk
        })
        self.assertTemplateUsed(response, 'promptarena/add-judge.html')
        self.assertContains(response, "This judge is already judging this contest", html=True)


    def test_add_judge_contest_closed(self):
        """Post an old story to a contest"""
        self.set_up_contest(ExternalJudgeContest)
        self.contest.status = Contest.CLOSED
        self.contest.save()
        response = self.client.post(reverse('add judge', kwargs = {'contest_id' : self.contest.pk}), {
            'judge' : self.user.pk
        })
        self.assertRedirects(response, '/1/view-contest-details')


    def test_enter_crit(self):
        """WEnter a crit in a contest"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.set_up_contest_components()
        self.contest.close()
        self.content=""
        self.crits = list(Crit.objects.filter(reviewer__username = 'djangotestuser1'))
        self.dummy_form = EnterCritForm()

        for i in range(self.dummy_form.wordcount_min):
            self.content += " word"
        self.login_testuser('djangotestuser1')
        response = self.client.post(reverse('judgemode', kwargs = {'crit_id': self.crits[0].pk}) , {
            'content': self.content,
            'score' : Crit.HI_SCORE,
            'final' : False,
            })
        self.assertRedirects(response, '/judgemode')

    def test_enter_crit_invalid(self):
        """Enter a crit in a contest with too few words"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.set_up_contest_components()
        self.contest.close()
        self.content=""
        self.crits = list(Crit.objects.filter(reviewer__username = 'djangotestuser1'))
        self.dummy_form = EnterCritForm()

        for i in range(self.dummy_form.wordcount_min-1):
            self.content += " word" + str(i)
        self.login_testuser('djangotestuser1')
        response = self.client.post(reverse('judgemode', kwargs = {'crit_id': self.crits[0].pk}) , {
            'content': self.content,
            'score' : Crit.HI_SCORE,
            'final' : False,
            })
        self.assertTemplateUsed(response, 'promptarena/judgemode.html')

    def test_enter_crit_with_repeat_score(self):
        """WEnter a crit in a contest"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.set_up_contest_components()
        self.contest.close()
        self.content=""
        self.crits = list(Crit.objects.filter(reviewer__username = 'djangotestuser1'))
        self.dummy_form = EnterCritForm()

        for i in range(self.dummy_form.wordcount_min):
            self.content += " word" + str(i)
        self.login_testuser('djangotestuser1')
        self.client.post(reverse('judgemode', kwargs = {'crit_id': self.crits[0].pk}) , {
            'content': self.content,
            'score' : Crit.HI_SCORE,
            'final' : False,
            })
        response = self.client.post(reverse('judgemode', kwargs = {'crit_id': self.crits[1].pk}) , {
            'content': self.content,
            'score' : Crit.HI_SCORE,
            'final' : False,
            })
        self.assertTemplateUsed(response, 'promptarena/judgemode.html')
        error_messages = []
        messages = list(response.context['messages'])
        for message in messages:
            if 'error' in message.tags:
                error_messages.append(message)

        self.assertEqual(len(error_messages), 1)
        self.assertIn('You have already used that rank in this contest', str(error_messages[0]))


