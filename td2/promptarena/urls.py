"""List of URLS for application"""
from django.urls import path
from . import views

urlpatterns = [
    #create things
    path('create-contest', views.create_contest, name='create contest'),
    path('<int:contest_id>/edit-contest', views.edit_contest, name='edit contest'),
    #view things
    path('<int:contest_id>/view-contest-details', views.view_contest_details, name='view contest details'),
    path('view-contests', views.view_contests, name='view contests'),
    path('<int:contest_id>/view-contest-judgement', views.view_contest_judgement, name='view contest judgement'),
    #enter things
    path('<int:contest_id>/enter-contest', views.enter_contest_new_story, name='enter contest'),
    path('<int:contest_id>/enter-contest-old-story', views.enter_contest_old_story, name='enter contest old story'),
    #judge things
    path('judgemode', views.judgemode, name='judgemode'),
    path('<int:crit_id>/judgemode', views.judgemode, name='judgemode'),
    #Do things by 'hand'
    path('<int:contest_id>/open-contest', views.open_contest, name='open contest'),
    path('<int:contest_id>/close-contest', views.close_contest, name='close contest'),
    path('<int:contest_id>/judge-contest', views.judge_contest, name='judge contest'),
]
