"""URLs for user registration, login, change activities"""
#from django.contrib import admin
#from django.views.generic import TemplateView
from django.urls import path
#from .views import (profile, signin, signup, p_logout, settings, change_password, change_email, activate,
#PassResetComplete, change_username, PassReset, PassResetDone, PassResetConfirm)

from .views import sign_up, profile, p_logout, settings, activate, set_timezone

urlpatterns = [
    path('signup/', sign_up, name='sign up'),
    path('profile/', profile, name='profile'),
    path('logout/', p_logout, name='logout'),
    path('set-timezone/', set_timezone, name="set timezone"),
    path('settings/', settings, name='change settings'),
    path('activate/<uidb64>/<token>/',activate, name='activate'),
]
