"""ADMIN files for baseapp"""
from django.contrib import admin  # pylint: disable=unused-import
from .models import Story, StoryStats

# Register your models here.

class StoryAdmin(admin.ModelAdmin):
    """Defines StoryAdmin Adminfields for admin screens

    Args:
        admin (ModelAdmin): a model for the admin screens
    """    """"""
    list_display = ("__str__", "access")

admin.site.register(Story, StoryAdmin)
admin.site.register(StoryStats)
