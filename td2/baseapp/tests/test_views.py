"""Test framework for users and profiles"""
from django.urls import reverse
from baseapp.tests.test_utils import BaseAppTestCase
# Create your tests here.


class BaseAppViewTest(BaseAppTestCase):
    """test views are available (login happens where needed)"""
    @classmethod
    def setUpTestData(cls):
        super(BaseAppViewTest, cls).setUpTestData()
        cls.set_up_story_private(cls)

    def test_home_view_exists(self):
        """test home view exists"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/home.html')

    def test_create_story_view_exists(self):
        """test create story view exists"""
        self.login_testuser('djangotestuser')
        response = self.client.get(reverse('create story'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/create-story.html')

    def test_edit_story_view_exists(self):
        """test edit story view exists"""
        self.login_testuser('djangotestuser')
        response = self.client.get(reverse('edit story' , kwargs = {"story_id": self.story.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/create-story.html')

    def test_view_story_by_slug_view_exists(self):
        """test view story by slug view exists"""
        self.login_testuser('djangotestuser')
        response = self.client.get(reverse('view story by slug', kwargs = {"author_slug":self.story.author.slug, "story_slug":self.story.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')

    def test_view_story_by_id_exists(self):
        """test view story by id exists"""
        self.login_testuser('djangotestuser')
        response = self.client.get(reverse('view story by id', kwargs = {"story_id":self.story.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')

    def test_view_stories_view_exists(self):
        """test view stories view exists"""
        response = self.client.get(reverse('view stories'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-stories.html')

    def test_view_stories_by_author_view_exists(self):
        """test stories by author view exists"""

        response = self.client.get(reverse('view stories by author', kwargs = {"author_slug":self.story.author.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-stories.html')

class BaseAppRestrictedViewByLogin(BaseAppTestCase):
    """test views restricted to logged in users are restricted"""
    @classmethod
    def setUpTestData(cls):
        super(BaseAppRestrictedViewByLogin, cls).setUpTestData()
        cls.set_up_story_private(cls)

    def test_create_story_view_restricted(self):
        """test create story  view login required"""
        response = self.client.get(reverse('create story'))
        #assertRedirects(response, expected_url, status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        self.assertRedirects(response, '/accounts/login/?next=/create-story')

    def test_edit_story_view_restricted(self):
        """test edit story view login required"""
        response = self.client.get(reverse('edit story', kwargs = {"story_id": self.story.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/1/edit-story')

    def test_view_story_by_id_restricted(self):
        """test view story by id login required"""
        response = self.client.get(reverse('view story by id', kwargs = {"story_id": self.story.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/1/view-story')

class BaseAppRestrictedViewByAuthorTest(BaseAppTestCase):
    """Test permissions when author has made various settings"""
    @classmethod
    def setUpTestData(cls):
        """Set up test data for class:
            author
            reader
        """
        super(BaseAppRestrictedViewByAuthorTest, cls).setUpTestData()
        cls.author = cls.User.objects.create_user(username='djangotestauthor', password='12345abcde')
        cls.reader = cls.User.objects.create_user(username='djangotestreader', password='12345abcde')
        cls.author.save()
        cls.reader.save()

    #test view story by ID

    def test_view_story_by_id_story_private(self):
        """test redirect for view story by id if:
         
         story private"""
        #user not logged in
        self.set_up_story_private()
        response = self.client.get(reverse('view story by id', kwargs = {"story_id": self.story.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/1/view-story')
        #log user in
        self.login_testuser('djangotestreader')
        response = self.client.get(reverse('view story by id', kwargs = {"story_id": self.story.pk}))
        self.assertRedirects(response, reverse('view stories'))

    def test_view_story_by_id_story_public(self):
        """test redirect for view story by id if:
         story public"""
         #user not logged in
        self.set_up_story_public()
        response = self.client.get(reverse('view story by id', kwargs = {"story_id": self.story.pk}))
        self.assertRedirects(response, '/accounts/login/?next=/1/view-story')
        #log user in
        self.login_testuser('djangotestreader')
        response = self.client.get(reverse('view story by id', kwargs = {"story_id": self.story.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')


    #Test view story by slug

    def test_view_story_by_slug_story_private(self):
        """test redirect for view story by slug if:
         
         story private"""
        #user not logged in
        self.set_up_story_private()
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.slug}))
        self.assertRedirects(response, reverse('view stories'))
        #log user in
        self.login_testuser('djangotestreader')
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.slug}))
        self.assertRedirects(response, reverse('view stories'))

    def test_view_story_by_slug_story_logged_in(self):
        """test redirect for view story by slug if:
         
         story public
         user not logged in"""
        self.set_up_story_logged_in()
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.slug}))
        self.assertRedirects(response, reverse('view stories'))
        #user logs in
        self.login_testuser('djangotestreader')
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')

    def test_view_story_by_slug_story_public(self):
        """test redirect for view story by slug if:
         
         story public
         user not logged in"""
        self.set_up_story_public()
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')
        #user logs in
        self.login_testuser('djangotestreader')
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')

    
  
   


        #Test author access

    def test_view_story_by_slug_story_private_user_author(self):
        """test redirect for view story by slug if:
         
         story private
         user  author"""
        self.set_up_story_private(self.author)
        self.login_testuser('djangotestauthor')
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')

    def test_view_story_by_slug_story_logged_in_user_author(self):
        """test redirect for view story by slug if:
         
         story public
         user  author"""
        self.login_testuser('djangotestauthor')
        self.set_up_story_public(author = self.author)
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')


    def test_view_story_by_slug_story_public_user_author(self):
        """test redirect for view story by slug if:
         
         story public
         user  author"""
        self.login_testuser('djangotestauthor')
        self.set_up_story_public(author = self.author)
        response = self.client.get(reverse('view story by slug', kwargs = {"story_slug": self.story.slug, "author_slug":self.story.author.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/view-story.html')







        #test edit story access

    def test_edit_story_user_author(self):
        """test redirect  edit story if:
         
         story private
         user  author"""
        self.set_up_story_private(self.author)
        self.login_testuser('djangotestauthor')
        response = self.client.get(reverse('edit story', kwargs = {"story_id": self.story.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'baseapp/create-story.html')

    def test_edit_story_user_not_author(self):
        """test redirect  edit story if:
         
         story private
         user not author"""
        self.set_up_story_private()
        self.login_testuser('djangotestreader')
        response = self.client.get(reverse('edit story', kwargs = {"story_id": self.story.pk}))
        self.assertRedirects(response, reverse('view stories'))

###TODO: Edit story entry test"""
