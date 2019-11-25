import datetime

from rest_framework.test import APITestCase

from core.models import MeasurementResult, Patient


class MeasurementResultTest(APITestCase):
    def test_is_sendable_true(self):
        p = Patient.objects.create(code='T00100000001', kakao_user_id='abc123', daily_measurement_count=1,
                                   measurement_noti_time_1=datetime.time(hour=8), measurement_noti_flag=True)
        m = p.create_measurement_result(noti_time_num=1)
        self.assertEqual(m.is_sendable(), True)

    def test_is_sendable_false(self):
        p = Patient.objects.create(code='T00100000001', kakao_user_id='abc123', daily_measurement_count=1,
                                   measurement_noti_time_1=datetime.time(hour=8), measurement_noti_flag=True)
        m = p.create_measurement_result(noti_time_num=1)
        m.set_success()
        self.assertEqual(m.is_sendable(), False)

    def test_get_status(self):
        p = Patient.objects.create(code='T00100000001', kakao_user_id='abc123', daily_measurement_count=1,
                                   measurement_noti_time_1=datetime.time(hour=8), measurement_noti_flag=True)
        m = p.create_measurement_result(noti_time_num=1)
        self.assertEqual(m.get_status(), MeasurementResult.STATUS.PENDING)

    def test_checked_true(self):
        p = Patient.objects.create(code='T00100000001', kakao_user_id='abc123', daily_measurement_count=1,
                                   measurement_noti_time_1=datetime.time(hour=8), measurement_noti_flag=True)
        m = p.create_measurement_result(noti_time_num=1)
        m.set_success()
        self.assertEqual(m.is_checked(), True)

    def test_checked_false(self):
        p = Patient.objects.create(code='T00100000001', kakao_user_id='abc123', daily_measurement_count=1,
                                   measurement_noti_time_1=datetime.time(hour=8), measurement_noti_flag=True)
        m = p.create_measurement_result(noti_time_num=1)
        self.assertEqual(m.is_checked(), False)

    def test_set_success(self):
        p = Patient.objects.create(code='T00100000001', kakao_user_id='abc123', daily_measurement_count=1,
                                   measurement_noti_time_1=datetime.time(hour=8), measurement_noti_flag=True)
        m = p.create_measurement_result(noti_time_num=1)
        m.set_success()
        m.save()
        self.assertEqual(m.get_status(), MeasurementResult.STATUS.SUCCESS)
