# Generated by Django 3.1.4 on 2020-12-21 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promptarena', '0002_auto_20201218_2004'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contest',
            name='title',
        ),
        migrations.AddField(
            model_name='contest',
            name='wordcount',
            field=models.PositiveIntegerField(default=1000),
        ),
    ]
