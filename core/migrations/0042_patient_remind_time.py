# Generated by Django 2.2.8 on 2023-11-25 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_auto_20230915_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='remind_time',
            field=models.TimeField(blank=True, null=True, verbose_name='리마인드 시간'),
        ),
    ]
