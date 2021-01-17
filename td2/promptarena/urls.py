"""List of URLS for application"""
from django.urls import path
from . import views

urlpatterns = [
    #create things
    path('create-prompt', views.create_prompt, name='create prompt'),
    path('<int:prompt_id>/edit-prompt', views.edit_prompt, name='edit prompt'),
    path('create-contest', views.create_contest_new_prompt, name='create contest'),
    path('create-contest-old-prompt', views.create_contest_old_prompt, name='create contest old prompt'),
    #view things
    path('<int:contest_id>/view-full-contest', views.view_full_contest, name='view full contest'),
    path('<int:contest_id>/close-contest', views.close_contest, name='close contest'),
    path('<int:contest_id>/open-contest', views.open_contest, name='open contest'),
    path('view-contests', views.view_contests, name='view contests'),
    path('view-prompts', views.view_prompts, name='view prompts'),
    path('<int:prompt_id>/view-full-prompt', views.view_full_prompt, name='view full prompt'),
    path('<int:contest_id>/view-judgement-contest', views.view_judgement_contest, name='view judgement contest'),

    #enter things
    path('<int:contest_id>/enter-contest', views.enter_contest, name='enter contest'),
    #path('enter-contest-old-story', views.enter-contest-old-story, name='enter contest old story"),
    #judge things
    path('judgemode', views.judgemode, name='judgemode'),
    path('<int:crit_id>/judgemode', views.judgemode, name='judgemode'),
    path('<int:contest_id>/judge-contest', views.judge_contest, name='judge contest'),


]
