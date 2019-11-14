import datetime
from enum import Enum

from django.contrib.postgres.fields import JSONField
from django.db import models
from datetime import timedelta

from core.models.helper import EnumField


class Patient(models.Model):
    class NotiType(Enum):
        MEDICATION = 'Medication'
        VISIT = 'Visit'
        MEASUREMENT = 'Measurement'

    class NotiTimeFields(Enum):
        MEDICATION = [
            'medication_noti_time_1', 'medication_noti_time_2', 'medication_noti_time_3', 'medication_noti_time_4',
            'medication_noti_time_5'
        ]
        MEASUREMENT = [
            'measurement_noti_time_1', 'measurement_noti_time_2', 'measurement_noti_time_3', 'measurement_noti_time_4',
            'measurement_noti_time_5'
        ]

    code = models.CharField(max_length=12, unique=True)
    hospital = models.ForeignKey('Hospital', on_delete=models.SET_NULL, related_name='patients', null=True)
    kakao_user_id = models.CharField(max_length=150, unique=True)
    nickname = models.CharField(max_length=20, default='')

    additionally_detected_flag = models.NullBooleanField(verbose_name='추가 균 검출 여부', null=True, default=None)
    additionally_detected_date = models.DateField(verbose_name='추가 균 검출일', null=True)
    treatment_started_date = models.DateField(verbose_name='치료 시작일', null=True)
    treatment_end_date = models.DateField(verbose_name='치료 종료일', null=True)
    discharged_flag = models.NullBooleanField(verbose_name='퇴원 여부', null=True, default=None)
    register_completed_flag = models.BooleanField(verbose_name='계정 등록 완료 여부', default=False)
    medication_manage_flag = models.NullBooleanField(verbose_name='복약관리 여부', null=True, default=None)
    daily_medication_count = models.IntegerField(verbose_name='하루 복약 횟수', default=0)
    medication_noti_flag = models.NullBooleanField(verbose_name='복약알림 여부', null=True, default=None)
    medication_noti_time_1 = models.TimeField(verbose_name='복약알림 시간 1', null=True, default=None)
    medication_noti_time_2 = models.TimeField(verbose_name='복약알림 시간 2', null=True, default=None)
    medication_noti_time_3 = models.TimeField(verbose_name='복약알림 시간 3', null=True, default=None)
    medication_noti_time_4 = models.TimeField(verbose_name='복약알림 시간 4', null=True, default=None)
    medication_noti_time_5 = models.TimeField(verbose_name='복약알림 시간 5', null=True, default=None)
    visit_manage_flag = models.NullBooleanField(verbose_name='내원관리 여부', null=True, default=None)
    next_visiting_date_time = models.DateTimeField(verbose_name='다음 내원일', null=True, default=None)
    visit_notification_flag = models.NullBooleanField(verbose_name='내원알림 여부', null=True, default=None)
    visit_notification_before = models.IntegerField(verbose_name='내원알림 시간', null=True, default=None)
    measurement_manage_flag = models.NullBooleanField(verbose_name='건강관리 여부', null=True, default=None)
    daily_measurement_count = models.IntegerField(verbose_name='하루 측정 횟수', default=0)
    measurement_noti_flag = models.NullBooleanField(verbose_name='측정 알림 여부', null=True, default=None)
    measurement_noti_time_1 = models.TimeField(verbose_name='측정 알림 시간 1', null=True, default=None)
    measurement_noti_time_2 = models.TimeField(verbose_name='측정 알림 시간 2', null=True, default=None)
    measurement_noti_time_3 = models.TimeField(verbose_name='측정 알림 시간 3', null=True, default=None)
    measurement_noti_time_4 = models.TimeField(verbose_name='측정 알림 시간 4', null=True, default=None)
    measurement_noti_time_5 = models.TimeField(verbose_name='측정 알림 시간 5', null=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '환자'
        verbose_name_plural = '환자'

    def __str__(self):
        return '%s/%s' % (self.code, self.nickname)

    def medication_noti_time_list(self):
        if not (self.measurement_manage_flag or self.medication_noti_flag):
            return list()

        time_list = [self.medication_noti_time_1, self.medication_noti_time_2, self.medication_noti_time_3,
                     self.medication_noti_time_4, self.medication_noti_time_5]
        return time_list[:self.daily_medication_count]

    def measurement_noti_time_list(self):
        if not (self.measurement_manage_flag or self.measurement_noti_flag):
            return list()

        time_list = [self.measurement_noti_time_1, self.measurement_noti_time_2, self.measurement_noti_time_3,
                     self.measurement_noti_time_4, self.measurement_noti_time_5]
        return time_list[:self.daily_measurement_count]

    def need_medication_noti_time_set(self):
        return None in self.medication_noti_time_list() and self.medication_noti_time_list() != []

    def next_undefined_medication_noti_time_number(self):
        if None in self.medication_noti_time_list():
            return self.medication_noti_time_list().index(None) + 1
        else:
            return None

    def need_measurement_noti_time_set(self):
        return None in self.measurement_noti_time_list() and self.measurement_noti_time_list() != []

    def next_undefined_measurement_noti_time_number(self):
        if None in self.measurement_noti_time_list():
            return self.measurement_noti_time_list().index(None) + 1
        else:
            return None

    def reset_medication(self):
        self.medication_manage_flag = None
        self.daily_medication_count = 0
        self.medication_noti_flag = None
        self.medication_noti_time_1 = None
        self.medication_noti_time_2 = None
        self.medication_noti_time_3 = None
        self.medication_noti_time_4 = None
        self.medication_noti_time_5 = None
        return self.save()

    def reset_visit(self):
        self.visit_manage_flag = None
        self.visit_notification_flag = None
        self.visit_notification_before = None
        self.medication_noti_time_1 = None
        self.medication_noti_time_2 = None
        self.medication_noti_time_3 = None
        self.medication_noti_time_4 = None
        self.medication_noti_time_5 = None
        return self.save()

    def reset_measurement_noti_time(self):
        self.measurement_noti_time_1 = None
        self.measurement_noti_time_2 = None
        self.measurement_noti_time_3 = None
        self.measurement_noti_time_4 = None
        self.measurement_noti_time_5 = None
        return self.save()

    def reset_measurement(self):
        self.measurement_manage_flag = None
        self.measurement_noti_flag = None
        self.daily_measurement_count = 0
        self.reset_measurement_noti_time()
        return self.save()

    def set_default_end_date(self):
        if self.treatment_started_date:
            self.treatment_end_date = self.treatment_started_date + timedelta(days=180)

    def next_visiting_date_time_str(self):
        dt = self.next_visiting_date_time.astimezone().strftime('%Y년 %m월 %d일 %p %I시 %M분')
        return dt.replace('PM', '오후').replace('AM', '오전')

    def hospital_code(self):
        if self.hospital:
            return self.hospital.code

    def is_medication_noti_sendable(self):
        return self.medication_manage_flag and self.medication_noti_flag

    def is_visit_noti_sendable(self):
        return self.visit_manage_flag and self.visit_notification_flag

    def is_measurement_noti_sendable(self):
        return self.measurement_manage_flag and self.measurement_noti_flag

    # def create_notification(self, type):


class Hospital(models.Model):
    code = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '병원/기관'
        verbose_name_plural = '병원/기관'

    def __str__(self):
        return f'{self.name}({self.code})'


class MedicationResult(models.Model):
    class Result(EnumField):
        PENDING = 'PENDING'
        SUCCESS = 'SUCCESS'
        DELAYED_SUCCESS = 'DELAYED_SUCCESS'
        NO_RESPONSE = 'NO_RESPONSE'
        FAILED = 'FAILED'
        SIDE_EFFECT = 'SIDE_EFFECT'

    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, related_name='medication_result', null=True)
    date = models.DateField(verbose_name='날짜', auto_now_add=True)
    medication_result_1 = models.CharField(max_length=2, verbose_name='1회차 복용 결과', choices=Result.choices(),
                                           default=Result.PENDING)
    medication_result_2 = models.CharField(max_length=2, verbose_name='2회차 복용 결과', choices=Result.choices(),
                                           default=Result.PENDING)
    medication_result_3 = models.CharField(max_length=2, verbose_name='3회차 복용 결과', choices=Result.choices(),
                                           default=Result.PENDING)
    medication_result_4 = models.CharField(max_length=2, verbose_name='4회차 복용 결과', choices=Result.choices(),
                                           default=Result.PENDING)
    medication_result_5 = models.CharField(max_length=2, verbose_name='5회차 복용 결과', choices=Result.choices(),
                                           default=Result.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MeasurementResult(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, related_name='measurement_result', null=True)
    measured_at = models.DateTimeField(verbose_name='날짜')
    oxygen_saturation = models.IntegerField(default=0, verbose_name='산소 포화도 측정 결과')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationRecord(models.Model):
    MAX_TRY_COUNT = 3

    class Status(EnumField):
        PENDING = 'PENDING'
        FAILED = 'FAILED'
        SUSPENDED = 'SUSPENDED'
        SENDING = 'SENDING'
        DELIVERED = 'DELIVERED'
        CANCELED = 'CANCELED'

    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='notification_records')
    status = models.CharField(max_length=15, choices=Status.choices(), default=Status.PENDING)
    recipient_number = models.CharField(max_length=50, verbose_name='수신인 번호')
    payload = JSONField()
    result = JSONField()
    tries_left = models.IntegerField(default=MAX_TRY_COUNT)
    reserved_at = models.DateTimeField()
    delivered_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_updated_at = models.DateTimeField(default=datetime.datetime.now())

    def send(self):
        if self.is_sendable():
            self.status = self.Status.SENDING
            self.tries_left -= 1
        #     TODO sending and receive result
        else:
            self.set_failed()

    def set_delivered(self):
        self.status = self.Status.DELIVERED
        self.delivered_at = datetime.datetime.now()
        self.status_updated_at = datetime.datetime.now()

    def cancel(self):
        self.status = self.Status.CANCELED
        self.tries_left = 0
        self.status_updated_at = datetime.datetime.now()

    # def suspend(self):
    # TODO not specified yet.

    def set_failed(self):
        self.status = self.Status.FAILED
        self.tries_left = 0
        self.status_updated_at = datetime.datetime.now()

    def is_sendable(self):
        return self.tries_left > 0 and \
               self.status in [self.Status.PENDING, self.Status.SUSPENDED] and \
               self.reserved_at > datetime.datetime.now()
