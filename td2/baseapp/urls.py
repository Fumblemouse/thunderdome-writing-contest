"""URLs used across the apps"""
from django.urls import path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from .views import home, create_story, edit_story, view_story_by_id, view_story_by_slug, view_stories, view_stories_by_author

urlpatterns = [
    path('', home, name='home'),
    path('create-story', create_story, name='create story'),
    path('<int:story_id>/edit-story', edit_story, name='edit story'),
    #path('<int:story_id>/view-story', view_story_by_id, name='view story by id'),
    #path('<slug:slug>/view-story', view_story_by_slug, name='view story by slug'),
    path('<slug:author_slug>/view-stories', view_stories_by_author, name='view stories by author'),
    path('<slug:author_slug>/<slug:story_slug>/read', view_story_by_slug, name='view story by slug'),


    path('view-stories', view_stories, name='view stories'),

    path('favicon.ico',
        RedirectView.as_view(
            url=staticfiles_storage.url('favicon.ico'),
            permanent=False),
        name="favicon"
    ),
]
