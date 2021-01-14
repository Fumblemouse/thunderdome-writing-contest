"""Test framework for users and profiles"""
from django.test import TestCase
from django.urls import reverse
# Create your tests here.
#things to check
#1. users can only get to create and edit stories if they are logged in
#2. users cannot view stories  if author has account as not viewable
#3. users cannot view stories  if author has story  as not viewable