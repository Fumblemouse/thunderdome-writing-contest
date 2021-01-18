"""Test models for Stories"""
from django.test import TestCase
from baseapp.models import Story

# Create your tests here.
class StoryModelTest(TestCase):
    """Test A Story"""
    def setUp(self):
        self.story = Story(title="My Story title")
    def test_story_string_representation(self):
        self.assertEqual(str(self.story), self.story.title)
    def test_story_verbose_name_plural(self):
        self.assertEqual(str(Story._meta.verbose_name_plural), "stories")
    def test_story_save_function(self):
        self.story.public_view_allowed = False
        self.story.save()
        self.assertTrue(self.story.slug == "my-story-title")
    def test_story_save_title_again_function(self):
        self.story.public_view_allowed = False
        self.story.title = "my changed title"
        self.story.save()
        self.assertTrue(self.story.slug == "my-changed-title")
    def test_story_wordcount(self):
        self.story.public_view_allowed = False
        self.story.content = "1 2 3 4 5 6 7 8 9 10"
        self.story.save()
        self.assertTrue(self.story.wordcount == 10)
