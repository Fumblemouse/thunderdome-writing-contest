"""Test framework for views in universal"""
from django.urls import reverse
#from django.utils import timezone
# Create your tests here.

#from promptarena.models import InternalJudgeContest, ExternalJudgeContest,Crit, Contest
#from promptarena.forms import  EnterCritForm
from baseapp.models import Story
from baseapp.utils import set_expirable_var, get_expirable_var
from baseapp.tests.test_utils import BaseAppTestCase
# Create your tests here.

class MiniDomeViewTest(BaseAppTestCase):
    """Test view is available"""

    def test_minidome_not_accessible_public(self):

        response = self.client.get(reverse('minidome'), follow = True)
        self.assertRedirects(response, '/')
        error_messages = []
        messages = list(response.context['messages'])
        for message in messages:
            if 'error' in message.tags:
                error_messages.append(message)

        self.assertEqual(len(error_messages), 1)
        self.assertIn('Not enough', str(error_messages[0]))

        self.set_up_story_public()

        response = self.client.get(reverse('minidome'), follow = True)
        self.assertRedirects(response, '/')
        error_messages = []
        messages = list(response.context['messages'])
        for message in messages:
            if 'error' in message.tags:
                error_messages.append(message)

        self.assertEqual(len(error_messages), 1)
        self.assertIn('Not enough', str(error_messages[0]))

    def test_minidome_not_accessible_logged_in(self):
        self.login_testuser()
        response = self.client.get(reverse('minidome'), follow = True)
        self.assertRedirects(response, '/')
        error_messages = []
        messages = list(response.context['messages'])
        for message in messages:
            if 'error' in message.tags:
                error_messages.append(message)

        self.assertEqual(len(error_messages), 1)
        self.assertIn('Not enough', str(error_messages[0]))

        self.set_up_story_logged_in()

        response = self.client.get(reverse('minidome'), follow = True)
        self.assertRedirects(response, '/')
        error_messages = []
        messages = list(response.context['messages'])
        for message in messages:
            if 'error' in message.tags:
                error_messages.append(message)

        self.assertEqual(len(error_messages), 1)
        self.assertIn('Not enough', str(error_messages[0]))


class MiniDomeTest(BaseAppTestCase):
    """test aspects of the minidome """
    @classmethod
    def setUpTestData(cls):
        """create a hundred public stories for use"""
        super(MiniDomeTest, cls).setUpTestData()
        cls.set_up_multiple_stories(cls)

    def test_minidome_accessible(self):
        """test minidome is available"""
        #self.set_up_minidome_public()
        response = self.client.get(reverse('minidome'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'universal/minidome.html')


    def test_minidome_shows_appropriate_stories_public(self):
        """Test all stories are public in public match"""
        self.response = self.client.get(reverse('minidome'))
        self.request = self.response.wsgi_request
        self.story_ids = get_expirable_var(self.request.session, 'minidome_stories', None)
        story_instance0 = Story.objects.get(pk = self.story_ids[0])
        story_instance1 = Story.objects.get(pk = self.story_ids[1])
        self.assertEqual(story_instance0.access, Story.PUBLIC)
        self.assertEqual(story_instance1.access, Story.PUBLIC)

    def test_minidome_shows_appropriate_stories_logged_in(self):
        """Test all stories are at least logged in access level in public match"""
        self.login_testuser()
        self.response = self.client.get(reverse('minidome'))
        self.request = self.response.wsgi_request
        self.story_ids = get_expirable_var(self.request.session, 'minidome_stories', None)
        story_instance0 = Story.objects.get(pk = self.story_ids[0])
        story_instance1 = Story.objects.get(pk = self.story_ids[1])
        self.assertTrue(story_instance0.access >= Story.LOGGED_IN)
        self.assertTrue(story_instance1.access >= Story.LOGGED_IN)

    def test_minidome_session_vars(self):
        """Test all stories are public in public match"""
        self.login_testuser()
        self.response = self.client.get(reverse('minidome'))
        self.request = self.response.wsgi_request
        self.story_ids1 = get_expirable_var(self.request.session, 'minidome_stories', None)
        del self.request.session['minidome_stories']
        response = self.client.get(reverse('minidome'))
        request = response.wsgi_request
        self.story_ids2 = get_expirable_var(request.session, 'minidome_stories', None)
        self.assertNotEqual(self.story_ids1, self.story_ids2)

    def test_minidome_judge_process(self):
        """ test judment creates scoress"""
        self.response = self.client.get(reverse('minidome'))
        self.request = self.response.wsgi_request
        self.story_ids = get_expirable_var(self.request.session, 'minidome_stories', None)
        response = self.client.post(reverse('minidome'), {
            'winner' : self.story_ids[0],
            'minidome_type': Story.PUBLIC,
        })
        story_instance0 = Story.objects.get(pk = self.story_ids[0])
        story_instance1 = Story.objects.get(pk = self.story_ids[1])
        self.assertTrue(story_instance0.stats.minidome_public_wins > 0)
        self.assertTrue(story_instance1.stats.minidome_public_losses > 0)
        self.assertRedirects(response, '/')

    def test_minidome_judge_limits(self):
        """ test suer blocked for period after submission"""
        self.login_testuser()
        response = self.client.get(reverse('minidome'))
        request = response.wsgi_request
        self.story_ids = get_expirable_var(request.session, 'minidome_stories', None)
        response = self.client.post(reverse('minidome'), {
            'winner' : self.story_ids[0],
            'minidome_type': Story.LOGGED_IN,
        })
        request = response.wsgi_request
        #follow = True becuase we reddirect but still want to read the messages
        response = self.client.get(reverse('minidome'), follow = True)
        request = response.wsgi_request

        self.judged_recently = get_expirable_var(request.session, 'minidome_judged', None)
        self.assertTrue(self.judged_recently)
        self.assertRedirects(response, '/')
        error_messages = []
        messages = list(response.context['messages'])
        for message in messages:
            if 'error' in message.tags:
                error_messages.append(message)

        self.assertEqual(len(error_messages), 1)
        self.assertIn('drunk with power', str(error_messages[0]))

    def test_minidome_bad_form(self):
        """Checks to see if invalid form handled"""
        """ test judment creates scoress"""
        self.response = self.client.get(reverse('minidome'))
        self.request = self.response.wsgi_request
        self.story_ids = get_expirable_var(self.request.session, 'minidome_stories', None)
        self.client.post(reverse('minidome'), {
            'winner' : 'a',
            'minidome_type': Story.PRIVATE,
        })
        story_instance0 = Story.objects.get(pk = self.story_ids[0])
        story_instance1 = Story.objects.get(pk = self.story_ids[1])
        self.assertFalse(story_instance0.stats.minidome_public_wins > 0)
        self.assertFalse(story_instance1.stats.minidome_public_losses > 0)
        #self.assertRedirects(response, '/')

    def test_minidome_uneven_stats_public(self):
        """checks to make sure process works if all scores are not 0"""
        self.set_up_minidome_public()
        self.set_up_minidome_logged_in()
        self.response = self.client.get(reverse('minidome'))
        self.request = self.response.wsgi_request
        self.story_ids = get_expirable_var(self.request.session, 'minidome_stories', None)
        response = self.client.post(reverse('minidome'), {
            'winner' : self.story_ids[0],
            'minidome_type': Story.PUBLIC,
        })
        story_instance0 = Story.objects.get(pk = self.story_ids[0])
        story_instance1 = Story.objects.get(pk = self.story_ids[1])
        self.assertTrue(story_instance0.stats.minidome_public_wins > 0)
        self.assertTrue(story_instance1.stats.minidome_public_losses > 0)
        self.assertRedirects(response, '/')

    def test_minidome_uneven_stats_logged_in(self):
        """checks to make sure process works if all scores are not 0"""
        self.set_up_minidome_public()
        self.set_up_minidome_logged_in()
        self.login_testuser()
        self.response = self.client.get(reverse('minidome'))
        self.request = self.response.wsgi_request
        self.story_ids = get_expirable_var(self.request.session, 'minidome_stories', None)
        response = self.client.post(reverse('minidome'), {
            'winner' : self.story_ids[0],
            'minidome_type': Story.PUBLIC,
        })
        story_instance0 = Story.objects.get(pk = self.story_ids[0])
        story_instance1 = Story.objects.get(pk = self.story_ids[1])
        self.assertTrue(story_instance0.stats.minidome_logged_in_wins > 0)
        self.assertTrue(story_instance1.stats.minidome_logged_in_losses > 0)
        self.assertRedirects(response, '/')



