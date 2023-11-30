import datetime

from django.contrib.postgres.fields import JSONField
from django.db import models

from core.models.helper.helper import EnumField

TODAY = datetime.datetime.now().astimezone().date()


class NotificationRecord(models.Model):
    MAX_TRY_COUNT = 3

    class STATUS(EnumField):
        PENDING = "PENDING"
        SENDING = "SENDING"
        RETRY = "RETRY"
        RESERVED = "RESERVED"
        DELIVERED = "DELIVERED"
        SUSPENDED = "SUSPENDED"
        FAILED = "FAILED"
        CANCELED = "CANCELED"

    patient = models.ForeignKey(
        "Patient", on_delete=models.CASCADE, related_name="notification_records"
    )
    medication_result = models.ForeignKey(
        "MedicationResult",
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="notification_records",
    )
    measurement_result = models.ForeignKey(
        "MeasurementResult",
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="notification_records",
    )
    biz_message_type = models.CharField(
        max_length=50, blank=True, null=True, default=None
    )
    noti_time_num = models.IntegerField(null=True, blank=True, default=None)
    status = models.CharField(
        max_length=20, choices=STATUS.choices(), default=STATUS.PENDING.value
    )
    recipient_number = models.CharField(max_length=50, verbose_name="수신인 번호")
    payload = JSONField(blank=True, null=True)
    result = JSONField(blank=True, null=True)
    tries_left = models.IntegerField(default=MAX_TRY_COUNT)
    send_at = models.DateTimeField()
    delivered_at = models.DateTimeField(blank=True, null=True)
    status_updated_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_status(self):
        if type(self.status) is str:
            return self.STATUS(self.status)
        return self.status

    def is_sendable(self):
        return (
            self.tries_left > 0
            and self.get_status()
            in [self.STATUS.PENDING, self.STATUS.SUSPENDED, self.STATUS.RETRY]
            and self.payload != {}
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

    def cancel(self):
        self.status = self.STATUS.CANCELED.value
        self.tries_left = 0
        self.status_updated_at = datetime.datetime.now().astimezone()
        self.save()

    def set_pending(self):
        self.status = self.STATUS.PENDING.value
        self.status_updated_at = datetime.datetime.now().astimezone()
        self.save()

    def set_retry(self):
        self.status = self.STATUS.RETRY.value
        self.status_updated_at = datetime.datetime.now().astimezone()
        self.save()

    def set_delivered(self):
        self.status = self.STATUS.DELIVERED.value
        self.delivered_at = datetime.datetime.now().astimezone()
        self.status_updated_at = datetime.datetime.now().astimezone()
        self.save()

    # def suspend(self):

    def set_failed(self):
        self.status = self.STATUS.FAILED.value
        self.tries_left = 0
        self.status_updated_at = datetime.datetime.now().astimezone()
        self.save()

    def build_biz_message_request(self):
        from core.tasks.util.biz_message import BizMessageBuilder

        biz_message = BizMessageBuilder(
            message_type=self.biz_message_type,
            patient=self.patient,
            date=TODAY,
            noti_time_num=self.noti_time_num,
        )
        self.payload = biz_message.to_dict()
