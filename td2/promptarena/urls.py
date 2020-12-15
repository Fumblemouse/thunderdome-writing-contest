"""List of URLS for application"""
from django.urls import path
from . import views

urlpatterns = [
    #enter things
    path('enter-prompt', views.enter_prompt, name='Enter Prompt'),
    path('enter-contest', views.enter_contest, name='Enter Contest'),
    path('<int:contest_id>/enter-story', views.enter_story, name='Enter Story'),
    #view things
    path('<int:contest_id>/view-full-contest', views.view_full_contest, name='View Full Contest'),
    path('view-current-contests', views.view_current_contests, name='View Current Contests'),
    path('<int:story_id>/view-story', views.view_story, name='View Story'),
    path('view-prompts', views.view_prompts, name='View Prompts'),
    ]
