# Generated by Django 3.1.7 on 2021-04-09 10:32

import autoslug.fields
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('bio', tinymce.models.HTMLField(blank=True)),
                ('private_profile', models.BooleanField(default=False, help_text='Check this to keep your work private from anyone except your fellow contestants.', verbose_name='Private profile')),
                ('highest_access', models.PositiveSmallIntegerField(choices=[(0, 'PRIVATE: Only your darkest heart'), (1, 'LOGGED-IN: Fellow users of taste and distinction'), (2, 'PUBLIC: The great unwashed')], default=2, help_text='Setting a value here will restrict all your stories to that                     level of privacy or more private. Eg, Selecting LOGGED-IN will make all of your PUBLIC                     stories only available to logged in users and prevent individual stories being set any higher.                     If this field is later set to a higher setting, individual stories                     will need their own privacy settings increased. Stories are Private by default', verbose_name='Restrict Story Sharing to:')),
                ('timezone', models.CharField(default='Pacific/Auckland', max_length=100)),
                ('slug', autoslug.fields.AutoSlugField(max_length=200)),
                ('wins', models.PositiveSmallIntegerField(default=0)),
                ('losses', models.PositiveSmallIntegerField(default=0)),
                ('hms', models.PositiveSmallIntegerField(default=0)),
                ('dms', models.PositiveSmallIntegerField(default=0)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
