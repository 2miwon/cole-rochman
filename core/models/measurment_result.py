from django.db import models


class MeasurementResult(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, related_name='measurement_results', null=True)
    date = models.DateField(verbose_name='날짜', auto_now_add=True)
    medication_time = models.IntegerField(verbose_name='복약 회차', null=True)
    measured_at = models.DateTimeField(verbose_name='날짜')
    oxygen_saturation = models.IntegerField(default=0, verbose_name='산소 포화도 측정 결과')
    notified_at = models.DateTimeField(null=True)
    checked_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

