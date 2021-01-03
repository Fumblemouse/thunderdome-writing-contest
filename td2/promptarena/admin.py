"""admin models"""
from django.contrib import admin # pylint: disable=unused-import

# Register your models here.
from .models import Prompt, Contest, Entry, Crit
admin.site.register(Prompt)
admin.site.register(Contest)
admin.site.register(Entry)
admin.site.register(Crit)
