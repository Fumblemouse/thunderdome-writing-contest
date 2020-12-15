"""URLs used across the apps"""
from django.urls import path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from .views import home
#from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', home, name='home'),
    path('favicon.ico',
        RedirectView.as_view(
            url=staticfiles_storage.url('favicon.ico'),
            permanent=False),
        name="favicon"
    ),
]
