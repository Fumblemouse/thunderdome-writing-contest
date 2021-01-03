"""URLs used across the apps"""
from django.urls import path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from .views import home, create_story, view_story_by_id, view_story_by_slug, view_stories, view_stories_by_author

urlpatterns = [
    path('', home, name='home'),
    path('create-story', create_story, name='create story'),
    path('<slug:slug>/view-story', view_story_by_slug, name='view story by slug'),
    path('<int:story_id>/view-story', view_story_by_id, name='view story by id'),
 
    path('view-stories', view_stories, name='view stories'),
    path('<str:username>/view-stories', view_stories_by_author, name='view stories by author'),
    path('favicon.ico',
        RedirectView.as_view(
            url=staticfiles_storage.url('favicon.ico'),
            permanent=False),
        name="favicon"
    ),
]
