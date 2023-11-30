from django.db import models
from datetime import datetime
from core.tasks.util.biz_message import TYPE


class NotificationTime(models.Model):
    class Meta:
        verbose_name = "복약 알림 시간"
        verbose_name_plural = "복약 알림 시간"

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
        verbose_name="복약 번호", default=1
    )  # 0 = reminder, 1 = 1회차, 2 = 2회차...
    activate = models.BooleanField(
        verbose_name="알림 활성화 여부", blank=False, null=False, default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    msg_type = models.CharField(
        max_length=20,
        choices=TYPE.choices(),
        default=TYPE.MEDICATION_NOTI,
    )

    def send(self) -> bool:
        import traceback
        from core.tasks.util.bizppurio.bizppurio import BizppurioRequest

        try:
            self.build_biz_message_request()
        except:
            self.result = traceback.format_exc()
            self.set_failed()
            self.save()
            return False

        if not self.is_sendable():
            if self.get_status() in [
                self.STATUS.PENDING,
                self.STATUS.SUSPENDED,
                self.STATUS.RETRY,
            ]:
                self.result = self.result or "NOT SENDABLE"
                self.set_failed()
                self.save()
            return False

        self.tries_left -= 1
        success, result = BizppurioRequest(payload=self.payload).send()

        if success:
            self.set_delivered()
        elif self.tries_left > 0:
            self.set_retry()
        else:
            self.set_failed()

        self.result = result
        self.save()
        return success
