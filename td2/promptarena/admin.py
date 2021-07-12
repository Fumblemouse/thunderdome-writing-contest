"""admin models"""
from django.contrib import admin  # pylint: disable=unused-import

# Register your models here.
from .models import Contest, Entry, Crit, InternalJudgeContest

admin.site.register(Contest)
admin.site.register(Entry)
admin.site.register(Crit)
admin.site.register(InternalJudgeContest)
