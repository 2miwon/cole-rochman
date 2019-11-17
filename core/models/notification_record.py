import datetime

from django.contrib.postgres.fields import JSONField
from django.db import models

from core.models.helper.helper import EnumField
from core.tasks.util.biz_message import BizMessage, TYPE, Message, Buttons


class NotificationRecord(models.Model):
    MAX_TRY_COUNT = 3

    class Status(EnumField):
        PENDING = 'PENDING'
        SENDING = 'SENDING'
        RESERVERD = 'RESERVED'
        DELIVERED = 'DELIVERED'
        SUSPENDED = 'SUSPENDED'
        FAILED = 'FAILED'
        CANCELED = 'CANCELED'

    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='notification_records')
    medication_record = models.ForeignKey('MedicationResult', null=True, default=None, on_delete=models.SET_NULL,
                                          related_name='notification_records')
    measurement_record = models.ForeignKey('MeasurementResult', null=True, default=None, on_delete=models.SET_NULL,
                                           related_name='notification_records')
    biz_message_type = models.CharField(max_length=50, null=True, default=None)
    status = models.CharField(max_length=15, choices=Status.choices(), default=Status.PENDING)
    recipient_number = models.CharField(max_length=50, verbose_name='수신인 번호')
    payload = JSONField()
    result = JSONField()
    tries_left = models.IntegerField(default=MAX_TRY_COUNT)
    send_at = models.DateTimeField()
    delivered_at = models.DateTimeField(null=True)
    status_updated_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # TODO
    # def build_biz_message_request(self):
    #     msg = Message(type=self.biz_message_type, patient=self.patient, noti_time=self.send_at)
    #     # btn = Buttons
    #     BizMessage(phone_number=self.recipient_number, message=msg)

    def is_sendable(self):
        return self.tries_left > 0 and \
               self.status in [self.Status.PENDING, self.Status.SUSPENDED] and \
               self.send_at > datetime.datetime.now()

    def send(self):
        if self.is_sendable():
            self.status = self.Status.SENDING
            self.tries_left -= 1
            self.save()
            #     TODO sending and receive result
        else:
            self.set_failed()

    def cancel(self):
        self.status = self.Status.CANCELED
        self.tries_left = 0
        self.status_updated_at = datetime.datetime.now()
        self.save()

    def set_delivered(self):
        self.status = self.Status.DELIVERED
        self.delivered_at = datetime.datetime.now()
        self.status_updated_at = datetime.datetime.now()
        self.save()

    # def suspend(self):
    # TODO not specified yet.

    def set_failed(self):
        self.status = self.Status.FAILED
        self.tries_left = 0
        self.status_updated_at = datetime.datetime.now()
        self.save()
