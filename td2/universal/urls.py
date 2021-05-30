"""List of URLS for application"""
from django.urls import path
from . import views

urlpatterns = [
    #
    path('minidome', views.minidome, name='minidome'),
]
