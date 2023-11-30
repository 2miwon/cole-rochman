from django.db import models
from datetime import datetime


class NotificationTimeTable(models.Model):
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.SET_NULL,
        related_name="notification_time_tables",
        blank=True,
        null=True,
    )
    notification_time = models.TimeField(
        verbose_name="복약알림 시간", blank=True, null=True, default=None
    )
    daily_num = models.IntegerField(
        verbose_name="복약 번호", default=0
    )  # 0 = reminder, 1 = 1회차, 2 = 2회차...
    activate = models.BooleanField(verbose_name="알림 활성화 여부", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
