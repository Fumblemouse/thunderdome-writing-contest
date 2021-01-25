"""Test framework for users and profiles"""
from django.test import TestCase
from django.urls import reverse
# Create your tests here.
from django.contrib.auth import get_user_model

from baseapp.models import Story
from promptarena.models
from baseapp.tests.test_utils import login_testuser, set_up_story_private, set_up_story_public
# Create your tests here.