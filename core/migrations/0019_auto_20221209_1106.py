# Generated by Django 2.2.8 on 2022-12-09 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20221208_1638'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='daily_measurement_count',
            field=models.IntegerField(default=0, verbose_name='하루 측정 횟수'),
        ),
        migrations.AddField(
            model_name='patient',
            name='measurement_manage_flag',
            field=models.NullBooleanField(default=None, verbose_name='건강관리 여부'),
        ),
        migrations.AddField(
            model_name='patient',
            name='measurement_noti_flag',
            field=models.NullBooleanField(default=None, verbose_name='측정 알림 여부'),
        ),
        migrations.AddField(
            model_name='patient',
            name='measurement_noti_time_1',
            field=models.TimeField(blank=True, default=None, null=True, verbose_name='측정 알림 시간 1'),
        ),
        migrations.AddField(
            model_name='patient',
            name='measurement_noti_time_2',
            field=models.TimeField(blank=True, default=None, null=True, verbose_name='측정 알림 시간 2'),
        ),
        migrations.AddField(
            model_name='patient',
            name='measurement_noti_time_3',
            field=models.TimeField(blank=True, default=None, null=True, verbose_name='측정 알림 시간 3'),
        ),
        migrations.AddField(
            model_name='patient',
            name='measurement_noti_time_4',
            field=models.TimeField(blank=True, default=None, null=True, verbose_name='측정 알림 시간 4'),
        ),
        migrations.AddField(
            model_name='patient',
            name='measurement_noti_time_5',
            field=models.TimeField(blank=True, default=None, null=True, verbose_name='측정 알림 시간 5'),
        ),
    ]