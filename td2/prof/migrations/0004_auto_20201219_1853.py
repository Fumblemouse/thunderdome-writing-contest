# Generated by Django 3.1.4 on 2020-12-19 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prof', '0003_auto_20201219_0115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='public_profile',
            field=models.BooleanField(blank=True, default=False, verbose_name='Display to non-logged-in users?'),
        ),
    ]