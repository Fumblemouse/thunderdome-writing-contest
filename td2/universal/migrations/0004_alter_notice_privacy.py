# Generated by Django 3.2.3 on 2021-06-25 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('universal', '0003_auto_20210624_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notice',
            name='privacy',
            field=models.PositiveSmallIntegerField(choices=[(1, 'LOGGED-IN - users of taste and distinction'), (2, 'PUBLIC - the great unwashed')], default=1),
        ),
    ]
