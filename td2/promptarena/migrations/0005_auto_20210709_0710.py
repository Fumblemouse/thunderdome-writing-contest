# Generated by Django 3.2.3 on 2021-07-08 19:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('baseapp', '0005_auto_20210613_1040'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('promptarena', '0004_auto_20210624_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='authors', to='profiles.customuser'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='entry',
            name='modified_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='contest',
            name='mode',
            field=models.CharField(choices=[('IC', 'Rumble'), ('EC', 'Judges'), ('BC', 'Brawl')], default='IC', max_length=2),
        ),
        migrations.AlterField(
            model_name='contest',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Unopened'), (1, 'Open for sign-ups'), (2, 'Judgement'), (3, 'Closed')], default=0),
        ),
        migrations.AlterField(
            model_name='entry',
            name='content',
            field=tinymce.models.HTMLField(blank=True),
        ),
        migrations.AlterField(
            model_name='entry',
            name='story',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='baseapp.story'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='title',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]