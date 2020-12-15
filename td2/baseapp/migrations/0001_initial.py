# Generated by Django 3.1.4 on 2020-12-14 02:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='no story title', max_length=200)),
                ('content', models.TextField(max_length=20000)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('public_view_allowed', models.BooleanField()),
                ('slug', models.SlugField(blank=True, default='no-story-slug', max_length=20, unique=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]