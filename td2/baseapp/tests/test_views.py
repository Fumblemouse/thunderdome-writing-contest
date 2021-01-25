"""Test framework for users and profiles"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from baseapp.models import Story
from baseapp.tests.test_utils import BaseAppTestCase
# Create your tests here.


class BaseAppViewTest(BaseAppTestCase):
    """test views are available (login happens where needed)"""
    @classmethod
    def setUpTestData(cls):
        cls.user = cls.create_testuser(cls)
        cls.user.save()
        cls.story = cls.set_up_story_private(cls)

    def test_home_view_exists(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/home.html')

    def test_create_story_view_exists(self):
        self.login_testuser('djangotestuser1')
        response = self.client.get(reverse('create story'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/create-story.html')

    def test_edit_story_view_exists(self):
        self.login_testuser('djangotestuser1')
        response = self.client.get(reverse('edit story' , kwargs = {"story_id": self.story.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/create-story.html')

    def test_view_story_by_slug_view_exists(self):
        self.login_testuser('djangotestuser1')
        response = self.client.get(reverse('view story by slug', kwargs = {"author_slug":self.story.author.profile.slug, "story_slug":self.story.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')

    def test_view_story_by_id_exists(self):
        self.login_testuser('djangotestuser1')
        response = self.client.get(reverse('view story by id', kwargs = {"story_id":self.story.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')

    def test_view_stories_view_exists(self):
        response = self.client.get(reverse('view stories'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-stories.html')

    def test_view_stories_by_author_view_exists(self):
        response = self.client.get(reverse('view stories by author', kwargs = {"author_slug":self.story.author.profile.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-stories.html')

class BaseAppRestrictedViewTByLoginest(BaseAppTestCase):
    """test views restricted to logged in users are restricted"""
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username='djangotestuser1', password='12345abcde')
        cls.user.save()
        cls.story = Story(title="My Story", content="This is a story all about how...", author = cls.user, public = False)
        cls.story.save()
    def test_create_story_view_restricted(self):
        response = self.client.get(reverse('create story'))
        #assertRedirects(response, expected_url, status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        self.assertRedirects(response, '/accounts/login/?next=/create-story')

    def test_edit_story_view_restricted(self):
        response = self.client.get(reverse('edit story', kwargs = {"story_id": self.story.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/1/edit-story')

    def test_view_story_by_id_restricted(self):
        response = self.client.get(reverse('view story by id', kwargs = {"story_id": self.story.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/1/view-story')

class BaseAppRestrictedViewByAuthorTest(BaseAppTestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username='djangotestauthor', password='12345abcde')
        cls.reader = User.objects.create_user(username='djangotestreader', password='12345abcde')
        cls.user.save()
        cls.reader.save()

    #test view story by ID

    def test_view_story_by_id_author_private_story_private_user_not_logged_in(self):
        self.set_up_story_private()
        response = self.client.get(reverse('view story by id', kwargs = {"story_id": self.story.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/1/view-story')

    def test_view_story_by_id_author_private_story_public_user_not_logged_in(self):
        """Should fail as author private beats story private"""
        self.set_up_story_public()
        response = self.client.get(reverse('view story by id', kwargs = {"story_id": self.story.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/1/view-story')

    def test_view_story_by_id_author_private_story_public_user_logged_in(self):
        self.login_testuser('djangotestreader')
        self.set_up_story_public()
        response = self.client.get(reverse('view story by id', kwargs = {"story_id": self.story.pk}))
        self.assertRedirects(response, reverse('view stories'))

    def test_view_story_by_id_author_private_story_private_user_logged_in(self):
        self.set_up_story_private()
        self.login_testuser('djangotestreader')
        response = self.client.get(reverse('view story by id', kwargs = {"story_id": self.story.pk}))
        self.assertRedirects(response, reverse('view stories'))

    def test_view_story_by_id_author_public_story_private_user_logged_in(self):
        self.set_up_story_private()
        print(self.user.profile.public_profile)
        self.user.profile.save()
        self.login_testuser('djangotestreader')
        response = self.client.get(reverse('view story by id', kwargs = {"story_id": self.story.pk}))
        self.assertRedirects(response, reverse('view stories'))

    def test_view_story_by_id_author_public_story_private_user_logged_in(self):
        self.set_up_story_private()
        self.user.profile.public_profile = True
        self.user.profile.save()
        self.login_testuser('djangotestreader')
        response = self.client.get(reverse('view story by id', kwargs = {"story_id": self.story.pk}))
        self.assertRedirects(response, reverse('view stories'))

    def test_view_story_by_id_author_public_story_public_user_logged_in(self):
        self.set_up_story_public()
        self.user.profile.public_profile = True
        self.user.profile.save()
        self.login_testuser('djangotestreader')
        response = self.client.get(reverse('view story by id', kwargs = {"story_id": self.story.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')

    #Test view story by slug

    def test_view_story_by_slug_author_private_story_private_user_not_logged_in(self):
        self.set_up_story_private()
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.profile.slug}))
        self.assertRedirects(response, reverse('view stories'))

    def test_view_story_by_slug_author_private_story_public_user_not_logged_in(self):
        """Should fail as author private beats story  private"""
        self.set_up_story_public()
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.profile.slug}))
        self.assertRedirects(response, reverse('view stories'))

    def test_view_story_by_slug_author_public_story_private_user_not_logged_in(self):
        self.set_up_story_private()
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.profile.slug}))
        self.assertRedirects(response, reverse('view stories'))

    def test_view_story_by_slug_author_public_story_public_user_not_logged_in(self):
        self.set_up_story_public()
        self.user.profile.public_profile = True
        self.user.profile.save()
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.profile.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')

    def test_view_story_by_slug_author_private_story_private_user_logged_in(self):
        self.set_up_story_private()
        self.login_testuser('djangotestreader')
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.profile.slug}))
        self.assertRedirects(response, reverse('view stories'))

    def test_view_story_by_slug_author_private_story_public_user_logged_in(self):
        self.set_up_story_public()
        self.login_testuser('djangotestreader')
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.profile.slug}))
        self.assertRedirects(response, reverse('view stories'))

    def test_view_story_by_slug_author_private_story_public_user_logged_in(self):
        self.login_testuser('djangotestreader')
        self.set_up_story_public()
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.profile.slug}))
        self.assertRedirects(response, reverse('view stories'))

    def test_view_story_by_slug_author_public_story_private_user_logged_in(self):
        """Should fail as author private beats story  private"""
        self.set_up_story_private()
        self.login_testuser('djangotestreader')
        self.user.profile.public_profile = True
        self.user.profile.save()
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.profile.slug}))
        self.assertRedirects(response, reverse('view stories'))

    def test_view_story_by_slug_author_public_story_public_user_logged_in(self):
        self.login_testuser('djangotestreader')
        self.set_up_story_public()
        self.user.profile.public_profile = True
        self.user.profile.save()
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.profile.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')

        #Test author access

    def test_view_story_by_slug_author_private_story_private_user_author(self):
        self.set_up_story_private()
        self.login_testuser('djangotestauthor')
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.profile.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')

    def test_view_story_by_slug_author_private_story_public_user_author(self):
        self.set_up_story_public()
        self.login_testuser( 'djangotestauthor')
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.profile.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')

    def test_view_story_by_slug_author_private_story_public_user_author(self):
        self.login_testuser( 'djangotestauthor')
        self.set_up_story_public()
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.profile.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')

    def test_view_story_by_slug_author_public_story_private_user_author(self):
        self.set_up_story_private()
        self.login_testuser('djangotestauthor')
        self.user.profile.public_profile = True
        self.user.profile.save()
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.profile.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')

    def test_view_story_by_slug_author_public_story_public_user_author(self):
        self.login_testuser('djangotestauthor')
        self.set_up_story_public()
        self.user.profile.public_profile = True
        self.user.profile.save()
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.profile.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')

        #test edit story access

    def test_edit_story_user_author(self):
        self.set_up_story_private()
        self.login_testuser('djangotestauthor')
        response = self.client.get(reverse('edit story', kwargs = {"story_id": self.story.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/create-story.html')

    def test_edit_story_user_not_author(self):
        self.set_up_story_private()
        self.login_testuser('djangotestreader')
        response = self.client.get(reverse('edit story', kwargs = {"story_id": self.story.pk}))
        self.assertRedirects(response, reverse('view stories'))

###TODO: Edit story entry test









