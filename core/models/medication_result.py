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
    status = models.CharField(max_length=20, choices=STATUS.choices(), default=STATUS.PENDING)
    status_info = models.TextField(max_length=100, verbose_name='이상 종류', default='')
    severity = models.IntegerField(verbose_name='이상 정도', blank=True, null=True)
    notified_at = models.DateTimeField(blank=True, null=True)
    checked_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def medication_noti_time_field_str(self):
        return 'medication_noti_time_%s' % self.medication_time

    def is_checked(self):
        return self.status not in [self.STATUS.PENDING, self.STATUS.NO_RESPONSE]

    def is_sendable(self):
        return self.status == self.STATUS.PENDING

    def is_notification_record_creatable(self):
        return self.is_sendable() and not self.notification_records.exists()

    def get_notification_record(self):
        return self.notification_records.get()

    def get_status(self):
        return self.status.value.split('.')[1]

    def set_no_response(self):
        self.status = self.STATUS.NO_RESPONSE
        self.notified_at = datetime.datetime.now().astimezone()
        self.save()

    def set_success(self):
        self.status = self.STATUS.SUCCESS
        self.checked_at = datetime.datetime.now().astimezone()
        self.save()

    def set_failed(self):
        self.status = self.STATUS.FAILED
        self.checked_at = datetime.datetime.now().astimezone()
        self.save()

    def set_delayed_success(self):
        self.status = self.STATUS.DELAYED_SUCCESS
        self.checked_at = datetime.datetime.now().astimezone()
        self.save()

    def set_side_effect(self, status_info, severity):
        self.status = self.STATUS.SIDE_EFFECT
        self.status_info = status_info
        self.severity = severity
        self.checked_at = datetime.datetime.now().astimezone()
        self.save()

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
