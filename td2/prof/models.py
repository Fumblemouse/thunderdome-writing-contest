"""Models from prof app"""
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """User settable details"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,)
    bio = models.TextField()
    public_profile = forms.BooleanField(default=False, verbose_name='Display to non-logged-in users?', required=False)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_profile_signal(sender, instance, created, **kwargs):
    """Signal to create/update links to profile"""
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
