"""admin models"""
from django.contrib import admin # pylint: disable=unused-import

# Register your models here.
from .models import MiniDome, Notice

admin.site.register(MiniDome)
admin.site.register(Notice)
