"""List of URLS for application"""
from django.urls import path
from . import views

urlpatterns = [
    #
    path("minidome", views.minidome, name="minidome"),
    path("minidome", views.minidome_logged_in, name="minidome loged in"),
    path("minidome", views.minidome_public, name="minidome public"),
]
