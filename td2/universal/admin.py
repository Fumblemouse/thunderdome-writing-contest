"""admin models"""
from django.contrib import admin # pylint: disable=unused-import

# Register your models here.
from .models import MiniDome, Notice

admin.site.register(MiniDome)

class NoticeAdmin(admin.ModelAdmin):
    fields = ('__str__', 'created')

admin.site.register(Notice)
