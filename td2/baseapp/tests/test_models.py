"""Test models for Stories"""
from django.test import TestCase
from baseapp.models import Story, StoryStats

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

    def test_story_creates_storystats(self):
        self.story.save()
        self.assertTrue(self.story.stats.minidome_public_wins == 0)

class StoryStatsModelTest(TestCase):
    """Tests for story stats (one to one model relationship  with story)"""
    def setUp(self):
        """Give 'em a  nice story"""
        self.story = Story(title="My Story title2")
        self.story.save()
        self.stats = None
    def test_storystats_save(self):
        """test the maths adds up after stats added"""
        self.stats = StoryStats(story = self.story,
            minidome_public_wins = 1,
            minidome_public_losses = 2,
            minidome_logged_in_wins = 3,
            minidome_logged_in_losses = 4,
        )
        self.stats.save()
        self.assertEqual(self.stats.minidome_total_logged_in_tests, 7)
        self.assertEqual(self.stats.minidome_total_public_tests, 3)
        self.assertEqual(self.stats.minidome_total_wins, 4)
        self.assertEqual(self.stats.minidome_total_losses, 6)

    def test_storystats_string_representation(self):
        """Test storystats returns title as string"""
        self.stats = StoryStats(story = self.story,
            minidome_public_wins = 1,
            minidome_public_losses = 2,
            minidome_logged_in_wins = 3,
            minidome_logged_in_losses = 4,
        )
        self.stats.save()
        self.assertEqual(str(self.stats), "stats for " + self.story.title)
