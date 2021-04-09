"""Test models for Stories"""
from django.test import TestCase
from baseapp.models import Story

# Create your tests here.
class StoryModelTest(TestCase):
    """Test A Story"""
    def setUp(self):
        self.story = Story(title="My Story title")
    def test_story_string_representation(self):
        """Test story returns title as string"""
        self.assertEqual(str(self.story), self.story.title)
    def test_story_verbose_name_plural(self):
        """Test story has verbose name"""
        self.assertEqual(str(Story._meta.verbose_name_plural), "stories")
    def test_story_save_function(self):
        """Test Story can save into database"""
        self.story.public = False
        self.story.save()
        self.assertTrue(self.story.slug == "my-story-title")

    def test_story_save_title_again_function(self):
        """Test story can update title"""
        self.story.public = False
        self.story.title = "my changed title"
        self.story.save()
        self.assertTrue(self.story.slug == "my-changed-title")

    def test_story_wordcount(self):
        """Test wordcount function"""
        self.story.public = False
        self.story.content = "1 2 3 4 5 6 7 8 9 10"
        self.story.save()
        self.assertTrue(self.story.wordcount == 10)
