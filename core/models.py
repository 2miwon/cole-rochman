from django.contrib.postgres.fields import JSONField
from django.db import models
from datetime import timedelta


class Patient(models.Model):
    code = models.CharField(max_length=12, unique=True)
    hospital = models.ForeignKey('Hospital', on_delete=models.SET_NULL, related_name='patients', null=True)
    kakao_user_id = models.CharField(max_length=150, unique=True)
    nickname = models.CharField(max_length=20, default='')

    treatment_started_date = models.DateField(verbose_name='치료 시작일', null=True)

    # add teatement_end_date
    treatment_end_date = models.DateField(verbose_name='치료 시작일', null=True)

    additionally_detected_flag = models.NullBooleanField(verbose_name='추가 균 검출 여부', null=True, default=None)
    additionally_detected_date = models.DateField(verbose_name='추가 균 검출일', null=True)
    discharged_flag = models.NullBooleanField(verbose_name='퇴원 여부', null=True, default=None)
    registered_flag = models.NullBooleanField(verbose_name='계정 등록 완료 여부', null=True, default=None)
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
    health_manage_flag = models.NullBooleanField(verbose_name='건강관리 여부', null=True, default=None)
    daily_measurement_count = models.IntegerField(verbose_name='하루 측정 횟수', default=0)
    measurement_noti_flag = models.NullBooleanField(verbose_name='측정 알림 여부', null=True, default=None)
    measurement_noti_time_1 = models.TimeField(verbose_name='측정 알림 시간 1', null=True, default=None)
    measurement_noti_time_2 = models.TimeField(verbose_name='측정 알림 시간 2', null=True, default=None)
    measurement_noti_time_3 = models.TimeField(verbose_name='측정 알림 시간 3', null=True, default=None)
    measurement_noti_time_4 = models.TimeField(verbose_name='측정 알림 시간 4', null=True, default=None)
    measurement_noti_time_5 = models.TimeField(verbose_name='측정 알림 시간 5', null=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s/%s' % (self.code, self.nickname)

    def medication_noti_time_list(self):
        if not (self.medication_manage_flag or self.medication_noti_flag):
            return list()

        time_list = [self.medication_noti_time_1, self.medication_noti_time_2, self.medication_noti_time_3,
                     self.medication_noti_time_4, self.medication_noti_time_5]
        return time_list[:self.daily_medication_count]

    def has_undefined_noti_time(self):
        # (medication_manage_flag == False or medication_noti_flag == False) -> return False
        return None in self.medication_noti_time_list()

    def next_undefined_noti_time_number(self):
        return self.medication_noti_time_list().index(None) + 1

    def reset_medication_noti(self):
        self.daily_medication_count = 0
        self.medication_noti_flag = None
        self.medication_noti_time_1 = None
        self.medication_noti_time_2 = None
        self.medication_noti_time_3 = None
        self.medication_noti_time_4 = None
        self.medication_noti_time_5 = None
        return self.save()

    class Meta:
        verbose_name = '환자'
        verbose_name_plural = '환자'

    def reset_visit_noti(self):
        self.visit_manage_flag = None
        self.medication_noti_time_1 = None
        self.medication_noti_time_2 = None
        self.medication_noti_time_3 = None
        self.medication_noti_time_4 = None
        self.medication_noti_time_5 = None
        return self.save()

    class Meta:
        verbose_name = '환자'
        verbose_name_plural = '환자'

    def set_default_end_date(self):
        if(self.treatment_started_date):
            self.treatment_end_date=self.treatment_started_date+timedelta(days=30)



class Hospital(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}({self.id})'

    class Meta:
        verbose_name = '병원'
        verbose_name_plural = '병원'


class Test(models.Model):
    data = JSONField()
    memo = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)

class MedicationResult(models.Model):
    # code = models.ForeignKey('Patient', on_delete=models.SET_NULL, related_name='code', null=True)
    code=models.CharField(max_length=12)
    date=models.DateField(verbose_name='날짜')
    medication_result_1 = models.IntegerField(default=0,verbose_name='복용 결과 1')
    medication_result_2 = models.IntegerField(default=0,verbose_name='복용 결과 2')
    medication_result_3 = models.IntegerField(default=0,verbose_name='복용 결과 3')
    medication_result_4 = models.IntegerField(default=0,verbose_name='복용 결과 4')
    medication_result_5 = models.IntegerField(default=0,verbose_name='복용 결과 5')

class MeasurementResult(models.Model):
    code = models.CharField(max_length=12)
    date = models.DateTimeFieldField(verbose_name='날짜')
    measurement_result=models.IntegerField(verbose_name='측정 결과')
