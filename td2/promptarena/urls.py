"""List of URLS for application"""
from django.urls import path
from . import views

urlpatterns = [
    #create things
    path('create-prompt', views.create_prompt, name='create prompt'),
    path('create-contest', views.create_contest, name='create contest'),
    #path('<int:contest_id>/enter-contest', views.enter_contest, name='enter contest'),
    #view things
    path('<int:contest_id>/view-full-contest', views.view_full_contest, name='view full contest'),
    path('view-current-contests', views.view_current_contests, name='view current contests'),
    path('<int:story_id>/view-story', views.view_story, name='View Story'),
    path('view-prompts', views.view_prompts, name='view prompts'),
    ]
