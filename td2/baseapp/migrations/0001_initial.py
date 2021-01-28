# Generated by Django 3.1.4 on 2021-01-28 02:14

import autoslug.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


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
                ('title', models.CharField(max_length=255)),
                ('content', tinymce.models.HTMLField()),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('access', models.PositiveSmallIntegerField(choices=[(0, 'Only your darkest heart'), (1, 'Logged-in users of taste and distinction'), (2, 'The great unwashed')], default=0, help_text='Caution: Making your story non-private will exclude it from entering contests', verbose_name='Who can see your story?')),
                ('slug', autoslug.fields.AutoSlugField(max_length=40, unique=True)),
                ('wordcount', models.PositiveSmallIntegerField()),
                ('has_been_public', models.BooleanField(default=False)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'stories',
            },
        ),
        migrations.AddConstraint(
            model_name='story',
            constraint=models.UniqueConstraint(fields=('title', 'author'), name='unique_titles_for_authors'),
        ),
    ]
