"""admin models"""
from django.contrib import admin # pylint: disable=unused-import

# Register your models here.
from .models import MiniDome

admin.site.register(MiniDome)
