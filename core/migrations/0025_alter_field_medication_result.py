# Generated by Django 2.2.6 on 2019-11-14 21:06

import core.models.models
import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_create_model_notification_record'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medicationresult',
            name='medication_result_1',
        ),
        migrations.RemoveField(
            model_name='medicationresult',
            name='medication_result_2',
        ),
        migrations.RemoveField(
            model_name='medicationresult',
            name='medication_result_3',
        ),
        migrations.RemoveField(
            model_name='medicationresult',
            name='medication_result_4',
        ),
        migrations.RemoveField(
            model_name='medicationresult',
            name='medication_result_5',
        ),
        migrations.AddField(
            model_name='medicationresult',
            name='checked_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='medicationresult',
            name='medication_time',
            field=models.IntegerField(null=True, verbose_name='복약 회차'),
        ),
        migrations.AddField(
            model_name='medicationresult',
            name='notified_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='medicationresult',
            name='status',
            field=models.CharField(choices=[('PENDING', 'PENDING'), ('SUCCESS', 'SUCCESS'), ('DELAYED_SUCCESS', 'DELAYED_SUCCESS'), ('NO_RESPONSE', 'NO_RESPONSE'), ('FAILED', 'FAILED'), ('SIDE_EFFECT', 'SIDE_EFFECT')], default=core.models.models.MedicationResult.Result('PENDING'), max_length=15),
        ),
        migrations.AlterField(
            model_name='measurementresult',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='measurement_results', to='core.Patient'),
        ),
        migrations.AlterField(
            model_name='medicationresult',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='medication_results', to='core.Patient'),
        ),
        migrations.AlterField(
            model_name='notificationrecord',
            name='status_updated_at',
            field=models.DateTimeField(default=datetime.datetime(2019, 11, 15, 6, 6, 10, 266310)),
        ),
        migrations.AlterField(
            model_name='profile',
            name='hospital',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profiles', to='core.Hospital'),
        ),
    ]
