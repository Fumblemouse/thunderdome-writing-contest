"""testing names of apps
"""
from django.test import TestCase

from baseapp.apps import BaseappConfig
from profiles.apps import ProfilesConfig
from promptarena.apps import PromptarenaConfig


class TestAppname(TestCase):
    """testing appname"""

    def test_appname(self):
        """testing appname"""
        self.assertTrue(BaseappConfig.name == "baseapp")
        self.assertTrue(PromptarenaConfig.name == "promptarena")
        self.assertTrue(ProfilesConfig.name == "profiles")
