import datetime
from django.utils import timezone
from enum import Enum
from django.core.validators import MaxValueValidator, MinValueValidator

from django.contrib.auth.models import User
from django.db import models
from django.db.models import F
from datetime import timedelta

from core.models.medication_result import MedicationResult


class Patient(models.Model):
    class NOTI_TYPE(Enum):
        MEDICATION = "Medication"
        VISIT = "Visit"

    class NOTI_TIME_FIELDS(Enum):
        MEDICATION = [
            "medication_noti_time_1",
            "medication_noti_time_2",
            "medication_noti_time_3",
            "medication_noti_time_4",
            "medication_noti_time_5",
        ]

    name = models.CharField(
        verbose_name="이름", max_length=10, default="", blank=True, null=True
    )
    gender = models.CharField(
        verbose_name="성별", max_length=10, default="", blank=True, null=True
    )
    birth = models.DateField(verbose_name="생년월일", blank=True, null=True)
    phone_number = models.CharField(
        verbose_name="전화번호", max_length=20, default="", blank=True, null=True
    )
    kakao_user_id = models.CharField(max_length=150, unique=True, null=True, blank=True)
    code = models.CharField(max_length=12, unique=True)
    hospital = models.ForeignKey(
        "Hospital", on_delete=models.SET_NULL, related_name="patients", null=True
    )
    nickname = models.CharField(max_length=20, default="", blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    safeout = models.NullBooleanField(verbose_name="외출 가능 여부", default=False)
    weight = models.DecimalField(
        verbose_name="몸무게", blank=True, null=True, max_digits=5, decimal_places=2
    )
    vision_left = models.DecimalField(
        verbose_name="왼쪽 시력", blank=True, null=True, max_digits=2, decimal_places=1
    )
    vision_right = models.DecimalField(
        verbose_name=" 오른쪽 시력", blank=True, null=True, max_digits=2, decimal_places=1
    )
    treatment_started_date = models.DateField(
        verbose_name="치료 시작일", blank=False, null=True
    )
    treatment_end_date = models.DateField(verbose_name="치료 종료일", blank=False, null=True)
    register_completed_flag = models.BooleanField(
        verbose_name="계정 등록 완료 여부", default=False
    )
    medication_manage_flag = models.NullBooleanField(
        verbose_name="복약관리 여부", blank=True, null=True, default=None
    )
    daily_medication_count = models.IntegerField(verbose_name="하루 복약 횟수", default=0)
    medication_noti_flag = models.NullBooleanField(
        verbose_name="복약알림 여부", blank=True, null=True, default=None
    )
    medication_noti_time_1 = models.TimeField(
        verbose_name="복약알림 시간 1", blank=True, null=True, default=None
    )
    medication_noti_time_2 = models.TimeField(
        verbose_name="복약알림 시간 2", blank=True, null=True, default=None
    )
    medication_noti_time_3 = models.TimeField(
        verbose_name="복약알림 시간 3", blank=True, null=True, default=None
    )
    medication_noti_time_4 = models.TimeField(
        verbose_name="복약알림 시간 4", blank=True, null=True, default=None
    )
    medication_noti_time_5 = models.TimeField(
        verbose_name="복약알림 시간 5", blank=True, null=True, default=None
    )
    visit_manage_flag = models.NullBooleanField(
        verbose_name="내원관리 여부", blank=True, null=True, default=None
    )
    next_visiting_date_time = models.DateTimeField(
        verbose_name="다음 내원일", blank=True, null=True, default=None
    )
    visit_notification_flag = models.NullBooleanField(
        verbose_name="내원알림 여부", blank=True, null=True, default=None
    )
    visit_notification_before = models.IntegerField(
        verbose_name="내원알림 시간", blank=True, null=True, default=None
    )
    display_dashboard = models.BooleanField(verbose_name="대쉬보드에서 보이기", default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "환자"
        verbose_name_plural = "환자"

    def __str__(self):
        return "%s/%s" % (self.code, self.name)
        # return '%s/%s' % (self.code, self.name or self.nickname)

    def save(self, *args, **kwargs):
        # Calculate treatment_end_date based on treatment_started_date
        if self.treatment_started_date and not self.treatment_end_date:
            self.treatment_end_date = self.treatment_started_date + timedelta(days=183)
        super().save(*args, **kwargs)

    def medication_noti_time_list_to_str(self):
        noti_list = [x for x in self.medication_noti_time_list() if x is not None]
        return ",".join([x.strftime("%H시 %M분") for x in noti_list])

    def medication_noti_time_list(self):
        if not (self.medication_noti_flag):
            return list()

        time_list = [
            self.medication_noti_time_1,
            self.medication_noti_time_2,
            self.medication_noti_time_3,
            self.medication_noti_time_4,
            self.medication_noti_time_5,
        ]
        return time_list[: self.daily_medication_count]

    def need_medication_noti_time_set(self):
        return (
            None in self.medication_noti_time_list()
            and self.medication_noti_time_list() != []
        )

    def next_undefined_medication_noti_time_number(self):
        if None in self.medication_noti_time_list():
            return self.medication_noti_time_list().index(None) + 1
        else:
            return None

    def next_undefined_measurement_noti_time_number(self):
        if None in self.measurement_noti_time_list():
            return self.measurement_noti_time_list().index(None) + 1
        else:
            return None

    def reset_medication_noti_time(self):
        self.medication_noti_time_1 = None
        self.medication_noti_time_2 = None
        self.medication_noti_time_3 = None
        self.medication_noti_time_4 = None
        self.medication_noti_time_5 = None
        self.save()

    def reset_medication(self):
        self.medication_manage_flag = None
        self.medication_noti_flag = None
        self.daily_medication_count = 0
        self.reset_medication_noti_time()
        self.save()

    def reset_visit(self):
        self.visit_manage_flag = None
        self.visit_notification_flag = None
        self.visit_notification_before = None
        self.medication_noti_time_1 = None
        self.medication_noti_time_2 = None
        self.medication_noti_time_3 = None
        self.medication_noti_time_4 = None
        self.medication_noti_time_5 = None
        self.save()

    def set_default_end_date(self):
        if (
            self.treatment_started_date
            and self.treatment_end_date is None
            or self.treatment_end_date == ""
        ):
            self.treatment_end_date = self.treatment_started_date + timedelta(days=183)

    def next_visiting_date_time_str(self):
        dt = self.next_visiting_date_time.astimezone().strftime(
            "%Y년 %m월 %d일 %p %I시 %M분"
        )
        return dt.replace("PM", "오후").replace("AM", "오전")

    def hospital_code(self):
        if self.hospital:
            return self.hospital.code

    def is_medication_noti_sendable(self):
        return self.medication_manage_flag and self.medication_noti_flag

    def is_visit_noti_sendable(self):
        return self.visit_manage_flag and self.visit_notification_flag

    def create_medication_result(
        self, noti_time_num: int, date=datetime.datetime.today().astimezone().date()
    ) -> MedicationResult:
        from core.serializers import MedicationResultSerializer

        if self.medication_manage_flag is False or self.medication_noti_flag is False:
            return

        noti_time = self.medication_noti_time_list()[noti_time_num - 1]

        data = {
            "patient": self.id,
            "date": date,
            "medication_time_num": noti_time_num,
            "medication_time": noti_time,
        }
        serializer = MedicationResultSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def code_hyphen(self):
        return self.code[:4] + "-" + self.code[4:]

    def get_age(self):
        return datetime.datetime.today().year - self.birthdate.year

    def get_korean_age(self):
        return datetime.datetime.today().year - self.birthdate.year + 1

    def get_noti_time_by_num(self, i: int):
        if i == 0:
            return self.medication_noti_time_1
        elif i == 1:
            return self.medication_noti_time_2
        elif i == 2:
            return self.medication_noti_time_3
        elif i == 3:
            return self.medication_noti_time_4
        elif i == 4:
            return self.medication_noti_time_5
        else:
            return None


class Sputum_Inspection(models.Model):
    patient_set = models.ForeignKey(Patient, on_delete=models.CASCADE)
    insp_date = models.DateField(verbose_name="검사 날짜", null=True)
    CHOICE_METHOD = ("객담", "객담"), ("기관지내시경 검체", "기관지내시경 검체"), ("기타", "기타")
    method = models.CharField(
        verbose_name="검체 종류", max_length=20, default="", choices=CHOICE_METHOD
    )
    CHOICE_TH = ("1차", "1차"), ("2차", "2차"), ("3차", "3차")
    th = models.CharField(
        verbose_name="검체 세부 분류", max_length=20, default="1차", choices=CHOICE_TH
    )
    CHOICE_SMEAR = (
        ("검사중", "검사중"),
        ("-", "-"),
        ("+-", "+-"),
        ("1+", "1+"),
        ("2+", "2+"),
        ("3+", "3+"),
        ("4+", "4+"),
        ("미시행", "미시행"),
    )
    smear_result = models.CharField(
        verbose_name="도말검사 결과", max_length=20, default="미시행", choices=CHOICE_SMEAR
    )
    CHOICE_CULTURE = (
        ("검사중", "검사중"),
        ("양성", "양성"),
        ("음성", "음성"),
        ("오염", "오염"),
        ("미시행", "미시행"),
    )
    culture_result = models.CharField(
        verbose_name="배양검사 결과", max_length=20, default="미시행", choices=CHOICE_CULTURE
    )
    deleted = models.BooleanField(verbose_name="삭제 여부", default=False)

    def __str__(self):
        return "%s/%s/%s/%s" % (
            self.method,
            self.th,
            self.smear_result,
            self.culture_result,
        )

    def get_date(self):
        return self.insp_date

    class Meta:
        verbose_name = "도말, 배양 검사"
        verbose_name_plural = "도말, 배양 검사"


class Pcr_Inspection(models.Model):
    patient_set = models.ForeignKey(Patient, on_delete=models.CASCADE)
    insp_date = models.DateField(verbose_name="검사 날짜", null=True)
    CHOICE_METHOD = ("객담", "객담"), ("기관지내시경 검체", "기관지내시경 검체"), ("기타", "기타")
    method = models.CharField(
        verbose_name="검사 방법", max_length=20, default="", choices=CHOICE_METHOD
    )
    CHOICE_PCR = ("양성", "양성"), ("음성", "음성")
    pcr_result = models.CharField(
        verbose_name="검사 결과", max_length=20, default="", choices=CHOICE_PCR
    )

    class Meta:
        verbose_name = "PCR 검사"
        verbose_name_plural = "PCR 검사"
