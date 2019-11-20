import datetime

from django.db import models

from core.models.helper.helper import EnumField


class MedicationResult(models.Model):
    class STATUS(EnumField):
        PENDING = 'PENDING'  # before notification sent
        NO_RESPONSE = 'NO_RESPONSE'
        SUCCESS = 'SUCCESS'
        DELAYED_SUCCESS = 'DELAYED_SUCCESS'
        FAILED = 'FAILED'
        SIDE_EFFECT = 'SIDE_EFFECT'

    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, related_name='medication_results', blank=True,
                                null=True)
    date = models.DateField(verbose_name='날짜')
    medication_time_num = models.IntegerField(verbose_name='복약 회차', blank=True, null=True)
    medication_time = models.TimeField(verbose_name='복약 회차(시간)', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS.choices(), default=STATUS.PENDING.value)
    status_info = models.TextField(max_length=100, verbose_name='이상 종류', default='', blank=True, null=True)
    severity = models.IntegerField(verbose_name='이상 정도', blank=True, null=True)
    notified_at = models.DateTimeField(verbose_name='알림 발송 시간', blank=True, null=True)
    checked_at = models.DateTimeField(verbose_name='확인 시간', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '복약 결과'
        verbose_name_plural = '복약 결과'

    def medication_noti_time_field_str(self):
        return 'medication_noti_time_%s' % self.medication_time

    def is_checked(self):
        return self.get_status() not in [self.STATUS.PENDING, self.STATUS.NO_RESPONSE]

    def is_sendable(self):
        return self.get_status() == self.STATUS.PENDING

    def is_notification_record_creatable(self):
        return self.is_sendable() and not self.notification_records.exists()

    def get_notification_record(self):
        return self.notification_records.get()

    def get_status(self):
        if type(self.status) is str:
            return self.STATUS(self.status)

        return self.status

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

    def set_side_effect(self, status_info, severity):
        self.status = self.STATUS.SIDE_EFFECT.value
        self.status_info = status_info
        self.severity = severity
        self.checked_at = datetime.datetime.now().astimezone()

    def create_notification_record(self):
        """
        :return: bool. success of failed
        """
        from core.models import NotificationRecord

        if not self.is_notification_record_creatable():
            return None

        data = {
            'patient': self.patient,
            'medication_record': self,
            'recipient_number': self.patient.phone_number,
            'send_at': datetime.datetime.combine(self.date, self.medication_time)
        }

        return NotificationRecord.objects.create(**data)
