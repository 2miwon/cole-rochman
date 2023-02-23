from django.contrib.auth.models import User
from django.db import models

from core.models import Patient


class Guardian(models.Model):
    patient_set = models.ForeignKey(Patient, on_delete=models.CASCADE)
    phone_number = models.CharField(verbose_name='전화번호', max_length=20, default='', blank=True, null=True)
    kakao_user_id = models.CharField(max_length=150, unique=True, null=True, blank=True)

    class Meta:
        verbose_name = '보호자'
        verbose_name_plural = '보호자'
