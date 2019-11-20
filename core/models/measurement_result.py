from django.db import models


class MeasurementResult(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, related_name='measurement_results', null=True)
    date = models.DateField(verbose_name='날짜', auto_now_add=True)
    measurement_time_num = models.IntegerField(verbose_name='측정 회차', blank=True, null=True)
    oxygen_saturation = models.IntegerField(default=0, verbose_name='산소 포화도 측정 결과')
    notified_at = models.DateTimeField(blank=True, null=True)
    measured_at = models.DateTimeField(verbose_name='확인 시간', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '산소포화도 측정 결과'
        verbose_name_plural = '산소포화도 측정 결과'
