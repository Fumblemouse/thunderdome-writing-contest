"""Test framework for users and profiles"""
from django.test import TestCase
from django.urls import reverse
# Create your tests here.
from django.contrib.auth import get_user_model
from profiles.models import Profile
