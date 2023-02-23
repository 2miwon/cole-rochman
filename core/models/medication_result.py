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
    date = models.DateField(verbose_name='날짜', auto_now_add=True)
    medication_time_num = models.IntegerField(verbose_name='복약 회차', blank=True, null=True)
    medication_time = models.TimeField(verbose_name='복약 회차(시간)', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS.choices(), default=STATUS.PENDING.value)
    symptom_name = models.TextField(max_length=100, verbose_name='이상 종류', default='', blank=True, null=True)
    symptom_severity1 = models.TextField(max_length=100, verbose_name='이상 정도1', blank=True, null=True)
    symptom_severity2 = models.TextField(max_length=100, verbose_name='이상 정도2', blank=True, null=True)
    symptom_severity3 = models.TextField(max_length=100, verbose_name='이상 정도3', blank=True, null=True)
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
        return self.is_sendable() and not self.notification_records.exists() and \
               self.medication_time and self.date

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
        print(self.status)
        if self.status != 'SIDE_EFFECT':
            print("1")
            self.status = self.STATUS.SUCCESS.value
        else:
            print("2")
#        self.status_info = ''
#        self.severity = None
#        self.symptom_name = ''
#        self.symptom_severity1 = ''
#        self.symptom_severity2 = ''
#        self.symptom_severity3 = ''
        self.checked_at = datetime.datetime.now().astimezone()

    def set_failed(self):
        self.status = self.STATUS.FAILED.value
        self.checked_at = datetime.datetime.now().astimezone()

    def set_delayed_success(self):
        self.status = self.STATUS.DELAYED_SUCCESS.value
        self.checked_at = datetime.datetime.now().astimezone()

    def set_side_effect(self, name, severity1, severity2, severity3):
        self.status = self.STATUS.SIDE_EFFECT.value
        self.symptom_name = name
        if severity1:
            self.symptom_severity1 = severity1
        if severity2:
            self.symptom_severity2 = severity2
        if severity3:
            self.symptom_severity3 = severity3
        self.checked_at = datetime.datetime.now().astimezone()

    def add_side_effect(self, name, severity1, severity2, severity3):
        self.status = self.STATUS.SIDE_EFFECT.value
        self.symptom_name += str("," + name)
        if severity1:
            self.symptom_severity1 += str("," + severity1)
        else:
            self.symptom_severity1 += str(",")
        if severity2:
            self.symptom_severity2 += str("," + severity2)
        else:
            self.symptom_severity2 += str(",")
        if severity3:
            self.symptom_severity3 += str("," + severity3)
        else:
            self.symptom_severity3 += str(",")
        self.checked_at = datetime.datetime.now().astimezone()


#    def set_side_effect(self, status_info, severity):
#        self.status = self.STATUS.SIDE_EFFECT.value
#        self.status_info = status_info
#        self.severity = severity
#        self.checked_at = datetime.datetime.now().astimezone()

    def create_notification_record(self, noti_time_num: int = None):
        """
        :return: bool. success of failed
        """
        from core.serializers import NotificationRecordSerializer
        from core.tasks.util.biz_message import TYPE

        if not self.is_notification_record_creatable():
            return None

        data = {
            'patient': self.patient.pk,
            'biz_message_type': TYPE.MEDICATION_NOTI.value,
            'medication_result': self.pk,
            'recipient_number': self.patient.phone_number,
            'send_at': datetime.datetime.combine(self.date, self.medication_time)
        }
        if noti_time_num:
            data['noti_time_num'] = noti_time_num

        serializer = NotificationRecordSerializer(data=data)
        if serializer.is_valid():
            return serializer.save()
        else:
            return serializer.errors
