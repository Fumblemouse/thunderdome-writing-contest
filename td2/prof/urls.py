"""URLs for user registration, login, change activities"""
#from django.contrib import admin
#from django.views.generic import TemplateView
from django.urls import path
from .views import (profile, signin, signup, p_logout, settings, change_password, change_email, activate,
PassResetComplete, change_username, PassReset, PassResetDone, PassResetConfirm)


urlpatterns = [
    path('profile/<str:username>/', profile, name='profile'),
    path('profile/', profile, name='profile'),
    path('login/', signin, name='login'),
    path('logout/', p_logout, name='logout'),
    path('signup/', signup, name='signup'),
    path('settings/', settings, name='settings'),
    path('change-email/', change_email, name='change email'),
    path('change-username/', change_username, name='change username'),
    path('change-password/', change_password, name='change password'),
    path('activate/<slug:uidb64>/<slug:token>/',
        activate, name='activate'),
    path('password-reset/', PassReset.as_view(), name='password reset'),               # password_reset/ -> change (password_reset/done/) when change this url
    path('password-reset/done/', PassResetDone.as_view(), name='password reset done'), # password_reset/done/ -> when change (password_reset/) make this url same and add (done/)
    path('reset/<slug:uidb64>/<slug:token>/',
         PassResetConfirm.as_view(), name='password reset confirm'),# reset/ -> change (reset/done/) when change this url
    path('reset/done/',
    PassResetComplete.as_view(), name='password reset complete'),  # reset/done/ -> when change (reset/) make this url same and add (done/)
]
