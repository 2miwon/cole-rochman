import datetime

from rest_framework.test import APITestCase

from core.models import Patient, Hospital, NotificationRecord
from core.tasks.notification import create_morning_notification, create_medication_notification, \
    create_measurement_notification
from core.tasks.util.biz_message import TYPE


def factory():
    h = Hospital.objects.create(name='test', code='A001')

    # MORNING_MEDI_MANAGEMENT_TRUE
    p1 = Patient.objects.create(
        code='A00100000001',
        hospital=h,
        nickname='user1',
        kakao_user_id='abc134',
        phone_number='01000000001',
        treatment_started_date=datetime.date.today() - datetime.timedelta(days=2),
        medication_manage_flag=True,
        medication_noti_flag=True,
        daily_medication_count=2,
        medication_noti_time_1=datetime.time(hour=8),
        medication_noti_time_2=datetime.time(hour=12),
        visit_manage_flag=True,
        visit_notification_flag=True,
        next_visiting_date_time=datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1),
                                                          datetime.time(hour=13)).astimezone(),
        visit_notification_before=3600,
        daily_measurement_count=2,
        measurement_manage_flag=True,
        measurement_noti_flag=True,
        measurement_noti_time_1=datetime.time(hour=8),
        measurement_noti_time_2=datetime.time(hour=12)
    )

    # MORNING_MEDI_MANAGEMENT_FALSE
    p2 = Patient.objects.create(
        code='A00100000002',
        hospital=h,
        nickname='user2',
        kakao_user_id='abc234',
        phone_number='01000000002',
        treatment_started_date=datetime.date.today() - datetime.timedelta(days=2),
        medication_manage_flag=False,
        visit_manage_flag=True,
        visit_notification_flag=True,
        next_visiting_date_time=datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1),
                                                          datetime.time(hour=13)).astimezone(),
        visit_notification_before=3600,
        measurement_manage_flag=False,
    )

    # MORNING_MEDI_MANAGEMENT_TRUE_AND_VISIT_TODAY
    p3 = Patient.objects.create(
        code='A00100000003',
        hospital=h,
        nickname='user3',
        kakao_user_id='abc323',
        phone_number='01000000003',
        treatment_started_date=datetime.date.today() - datetime.timedelta(days=2),
        medication_manage_flag=True,
        medication_noti_flag=True,
        daily_medication_count=2,
        medication_noti_time_1=datetime.time(hour=8),
        medication_noti_time_2=datetime.time(hour=12),
        visit_manage_flag=True,
        visit_notification_flag=True,
        next_visiting_date_time=datetime.datetime.combine(datetime.date.today(), datetime.time(hour=13)).astimezone(),
        visit_notification_before=3600 * 2,
        daily_measurement_count=2,
        measurement_manage_flag=True,
        measurement_noti_flag=True,
        measurement_noti_time_1=datetime.time(hour=8),
        measurement_noti_time_2=datetime.time(hour=12)
    )

    # MORNING_MEDI_MANAGEMENT_FALSE_AND_VISIT_TODAY
    p4 = Patient.objects.create(
        code='A00100000004',
        hospital=h,
        nickname='user4',
        kakao_user_id='abc434',
        phone_number='01000000004',
        treatment_started_date=datetime.date.today() - datetime.timedelta(days=2),
        medication_manage_flag=False,
        visit_manage_flag=True,
        visit_notification_flag=True,
        next_visiting_date_time=datetime.datetime.combine(datetime.date.today(), datetime.time(hour=13)).astimezone(),
        visit_notification_before=3600 * 2,
        measurement_manage_flag=False,
    )
    return p1, p2, p3, p4


class NotificationTest(APITestCase):
    def test_create_morning_notification(self):
        p1, p2, p3, p4 = factory()
        create_morning_notification()
        queryset = NotificationRecord.objects.all()

        self.assertEqual(queryset.get(patient=p1).biz_message_type, TYPE.MORNING_MEDI_MANAGEMENT_TRUE.value)
        self.assertEqual(queryset.get(patient=p2).biz_message_type, TYPE.MORNING_MEDI_MANAGEMENT_FALSE.value)
        self.assertEqual(queryset.get(patient=p3).biz_message_type,
                         TYPE.MORNING_MEDI_MANAGEMENT_TRUE_AND_VISIT_TODAY.value)
        self.assertEqual(queryset.get(patient=p4).biz_message_type,
                         TYPE.MORNING_MEDI_MANAGEMENT_FALSE_AND_VISIT_TODAY.value)
        for obj in queryset:
            self.assertEqual(obj.is_sendable(), True)

    def test_create_medication_notification(self):
        p1, p2, p3, p4 = factory()
        create_medication_notification()
        queryset = NotificationRecord.objects.all()

        today = datetime.date.today()
        self.assertEqual(
            (queryset.filter(patient=p1)[0].send_at.astimezone(), queryset.filter(patient=p1)[1].send_at.astimezone()),
            (datetime.datetime.combine(today, p1.medication_noti_time_1).astimezone(),
             datetime.datetime.combine(today, p1.medication_noti_time_2).astimezone())
        )
        self.assertEqual(
            (queryset.filter(patient=p3)[0].send_at.astimezone(), queryset.filter(patient=p3)[1].send_at.astimezone()),
            (datetime.datetime.combine(today, p3.medication_noti_time_1).astimezone(),
             datetime.datetime.combine(today, p3.medication_noti_time_2).astimezone())
        )

        self.assertEqual(queryset.filter(patient=p2).count(), 0)
        self.assertEqual(queryset.filter(patient=p4).count(), 0)
        for obj in queryset:
            self.assertEqual(obj.is_sendable(), True)

    def test_create_measurement_notification(self):
        p1, p2, p3, p4 = factory()
        create_measurement_notification()
        queryset = NotificationRecord.objects.all()

        today = datetime.date.today()
        self.assertEqual(
            (queryset.filter(patient=p1)[0].send_at.astimezone(), queryset.filter(patient=p1)[1].send_at.astimezone()),
            (datetime.datetime.combine(today, p1.measurement_noti_time_1).astimezone(),
             datetime.datetime.combine(today, p1.measurement_noti_time_2).astimezone())
        )
        self.assertEqual(
            (queryset.filter(patient=p3)[0].send_at.astimezone(), queryset.filter(patient=p3)[1].send_at.astimezone()),
            (datetime.datetime.combine(today, p3.measurement_noti_time_1).astimezone(),
             datetime.datetime.combine(today, p3.measurement_noti_time_2).astimezone())
        )

        self.assertEqual(queryset.filter(patient=p2).count(), 0)
        self.assertEqual(queryset.filter(patient=p4).count(), 0)
        for obj in queryset:
            self.assertEqual(obj.is_sendable(), True)
