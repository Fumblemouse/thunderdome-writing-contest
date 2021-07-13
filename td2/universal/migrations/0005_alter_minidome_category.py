# Generated by Django 3.2.3 on 2021-07-13 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('universal', '0004_alter_notice_privacy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='minidome',
            name='category',
            field=models.PositiveSmallIntegerField(choices=[(1, 'LOGGED-IN - users of taste and distinction'), (2, 'PUBLIC - the great unwashed')], default=2, verbose_name='Category'),
        ),
    ]
