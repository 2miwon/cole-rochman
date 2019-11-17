from django.db import models

from core.models.helper.helper import EnumField
from core.serializers import NotificationRecordSerializer


class MedicationResult(models.Model):
    class Status(EnumField):
        PENDING = 'PENDING'
        SUCCESS = 'SUCCESS'
        DELAYED_SUCCESS = 'DELAYED_SUCCESS'
        NO_RESPONSE = 'NO_RESPONSE'
        FAILED = 'FAILED'
        SIDE_EFFECT = 'SIDE_EFFECT'

    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, related_name='medication_results', null=True)
    date = models.DateField(verbose_name='날짜', auto_now_add=True)
    medication_time = models.IntegerField(verbose_name='복약 회차', null=True)
    status = models.CharField(max_length=15, choices=Status.choices(), default=Status.PENDING)
    status_info = models.TextField(verbose_name='이상 종류', default='')
    severity = models.IntegerField(verbose_name='이상 정도', null=True)
    notified_at = models.DateTimeField(null=True)
    checked_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def medication_noti_time_field_str(self):
        return 'medication_noti_time_%s' % self.medication_time

    def is_sendable(self):
        return self.status == self.Status.PENDING or self.notification_records is not None

    def get_notification_record(self):
        return self.notification_records.get()

    def create_notification_record(self):
        """
        :return: bool. success of failed
        """
        if not self.is_sendable() or not self.notification_records.exists():
            return None
        data = {
            'patient': self.patient,
            'medication_record': self,
            'recipient_number': self.patient.phone_number
        }

        serializer = NotificationRecordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return obj
