# Generated by Django 3.2 on 2021-04-12 02:29

import autoslug.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('baseapp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, unique=True)),
                ('content', tinymce.models.HTMLField()),
                ('start_date', models.DateTimeField(verbose_name='Start Date')),
                ('expiry_date', models.DateTimeField(verbose_name='Submit by Date')),
                ('mode', models.CharField(choices=[('INTERNAL JUDGE CONTEST', 'Internal Judge Contest'), ('EXTERNAL JUDGE CONTEST', 'External Judge Contest')], default='INTERNAL JUDGE CONTEST', max_length=22)),
                ('status', models.CharField(choices=[('UNOPENED', 'Unopened'), ('OPEN', 'Open'), ('JUDGEMENT', 'Judgement'), ('CLOSED', 'Closed')], default='UNOPENED', max_length=9)),
                ('max_wordcount', models.PositiveIntegerField(default=1000)),
                ('entrant_num', models.PositiveSmallIntegerField(default=0)),
                ('slug', autoslug.fields.AutoSlugField(max_length=200, unique=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contests', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveSmallIntegerField(default=0)),
                ('score', models.PositiveSmallIntegerField(default=0)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=255)),
                ('content', tinymce.models.HTMLField()),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='promptarena.contest')),
                ('story', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='baseapp.story')),
            ],
            options={
                'verbose_name_plural': 'entries',
            },
        ),
        migrations.CreateModel(
            name='Crit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', tinymce.models.HTMLField(help_text='Please enter your comments here')),
                ('score', models.IntegerField(choices=[(0, 'Select Score'), (3, 'Low'), (5, 'Low Middle'), (7, 'Middle'), (11, 'High Middle'), (13, 'High')], default=0)),
                ('final', models.BooleanField(default=False, help_text='Check this box if you are finished with your critique. Be warned! - once submitted with this box checked no further edits can be made.')),
                ('wordcount', models.PositiveIntegerField(default=100, null=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('entry', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='crits', to='promptarena.entry')),
                ('reviewer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='crits', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ContestJudges',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='judges', to='promptarena.contest')),
                ('judge', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='judges', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='contest',
            name='judge',
            field=models.ManyToManyField(blank=True, through='promptarena.ContestJudges', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Brawl',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('promptarena.contest',),
        ),
        migrations.CreateModel(
            name='ExternalJudgeContest',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('promptarena.contest',),
        ),
        migrations.CreateModel(
            name='InternalJudgeContest',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('promptarena.contest',),
        ),
    ]
