"""URLs used across the apps"""
from django.urls import path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from .views import home, create_story

urlpatterns = [
    path('', home, name='home'),
    path('create-story', create_story, name='create story'),
    path('favicon.ico',
        RedirectView.as_view(
            url=staticfiles_storage.url('favicon.ico'),
            permanent=False),
        name="favicon"
    ),
]
