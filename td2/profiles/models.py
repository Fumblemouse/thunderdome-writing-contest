"""Models from profiles app"""
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.text import slugify
from autoslug import AutoSlugField
from tinymce import models as tinymce_models



class Profile(models.Model):
    """User settable details"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,)
    bio = tinymce_models.HTMLField(blank=True, )
    public_profile = models.BooleanField(
        default=False,
        help_text='Leave this unchecked to keep your work private from anyone except necessary contestants.'
        '<em>NB:</em> If checked, you will still  need to set public visibility on each story',
        verbose_name='Public?',
    )
    timezone = models.CharField(default="Pacific/Auckland", max_length=100)
    slug = AutoSlugField(max_length=200)

    def __str__(self):
        return self.user.username

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        slug = self.slug
        if not self.pk or slug=='':
            self.slug = slugify(self.user.username)
        return super(Profile, self).save()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_profile_signal(sender, instance, created, **kwargs): # pylint: disable=unused-argument
    """Signal to create/update links to profile"""
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
