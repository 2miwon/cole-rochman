# Generated by Django 2.2.6 on 2019-10-07 14:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_test'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
