import datetime

from django.db import models

from core.models.helper.helper import EnumField


class MeasurementResult(models.Model):
    class STATUS(EnumField):
        PENDING = 'PENDING'  # before notification sent
        NO_RESPONSE = 'NO_RESPONSE'
        SUCCESS = 'SUCCESS'
        DELAYED_SUCCESS = 'DELAYED_SUCCESS'
        FAILED = 'FAILED'

    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, related_name='measurement_results', null=True)
    date = models.DateField(verbose_name='날짜', auto_now_add=True)
    measurement_time_num = models.IntegerField(verbose_name='측정 회차', blank=True, null=True)
    measurement_time = models.TimeField(verbose_name='측정 회차(시간)', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS.choices(), default=STATUS.PENDING.value)
    oxygen_saturation = models.IntegerField(default=0, verbose_name='산소 포화도 측정 결과')
    notified_at = models.DateTimeField(blank=True, null=True)
    measured_at = models.DateTimeField(verbose_name='확인 시간', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '산소포화도 측정 결과'
        verbose_name_plural = '산소포화도 측정 결과'

    def get_status(self):
        if type(self.status) is str:
            return self.STATUS(self.status)

        return self.status

    def is_checked(self):
        return self.get_status() not in [self.STATUS.PENDING, self.STATUS.NO_RESPONSE]

    def is_sendable(self):
        return self.get_status() == self.STATUS.PENDING

    def is_notification_record_creatable(self):
        return self.is_sendable() and not self.notification_records.exists()

    def set_no_response(self):
        self.status = self.STATUS.NO_RESPONSE.value
        self.notified_at = datetime.datetime.now().astimezone()

    def set_success(self):
        self.status = self.STATUS.SUCCESS.value
        self.checked_at = datetime.datetime.now().astimezone()

    def set_failed(self):
        self.status = self.STATUS.FAILED.value
        self.checked_at = datetime.datetime.now().astimezone()

    def set_delayed_success(self):
        self.status = self.STATUS.DELAYED_SUCCESS.value
        self.checked_at = datetime.datetime.now().astimezone()

    def create_notification_record(self):
        from core.serializers import NotificationRecordSerializer
        from core.tasks.util.biz_message import TYPE

        if not self.is_notification_record_creatable():
            return None

        data = {
            'patient': self.patient.pk,
            'biz_message_type': TYPE.MEASUREMENT_NOTI.value,
            'measurement_result': self.pk,
            'recipient_number': self.patient.phone_number,
            'send_at': datetime.datetime.combine(self.date, self.measurement_time)
        }

        serializer = NotificationRecordSerializer(data=data)
        if serializer.is_valid():
            return serializer.save()
        else:
            return serializer.errors
