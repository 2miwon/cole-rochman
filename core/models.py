from django.contrib.postgres.fields import JSONField
from django.db import models


class Patient(models.Model):
    code = models.CharField(max_length=12, unique=True)
    kakao_user_id = models.CharField(max_length=150)
    nickname = models.CharField(max_length=20, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s/%s' % (self.code, self.nickname)

    class Meta:
        verbose_name = '환자'
        verbose_name_plural = '환자'


class Test(models.Model):
    data = JSONField()
    memo = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)