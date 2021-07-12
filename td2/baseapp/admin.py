"""ADMIN files for baseapp"""
from django.contrib import admin  # pylint: disable=unused-import
from .models import Story, StoryStats

# Register your models here.

admin.site.register(Story)
admin.site.register(StoryStats)
