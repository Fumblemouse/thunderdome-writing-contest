"""admin models"""
from django.contrib import admin  # pylint: disable=unused-import

# Register your models here.
from .models import MiniDome, Notice

admin.site.register(MiniDome)


class NoticeAdmin(admin.ModelAdmin):
    """Defines NoticeAdmin Adminfields for admin screens

    Args:
        admin (ModelAdmin): a model for the admin screens
    """    """"""
    fields = ("__str__", "created")


admin.site.register(Notice)
