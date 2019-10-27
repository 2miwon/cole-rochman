import datetime
import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from parameterized import parameterized
from django.utils import timezone

from core.models import Patient, Test

time_request_example_1am = '{"timeHeadword": "am", "hour": "1", "second": null, "timeTag": "am", "time": "01:00:00", "date": "2019-10-16", "minute": null}'
date_time_request_example = '{"dateTag": null, "timeHeadword": "pm", "hour": null, "dateHeadword": null, "time": "15:00:00",\
          "second": null, "month": "11", "timeTag": "pm", "year": null, "date": "2019-11-01", "day": "1", "minute": null}'


class PatientCreateTest(APITestCase):
    def test_create_success(self):
        """
        create patient
        """
        url = reverse('patient-create')
        data = {
            'userRequest': {'user': {'id': 'asd123'}},
            'action': {'params': {'patient_code': 'test'}}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(Patient.objects.get().code, 'test')
        self.assertEqual(Patient.objects.get().kakao_user_id, 'asd123')

    def test_create_success_when_test_true(self):
        """
        create patient when request.queryparams's test value is true.
        It results not actually saving it, but it will respond with serializer's data
        """
        url = reverse('patient-create')
        data = {
            'userRequest': {'user': {'id': 'asd123'}},
            'action': {'params': {'patient_code': 'test'}}
        }

        response = self.client.post(url + '?test=true', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['test'], True)
        self.assertEqual(Patient.objects.count(), 0)


class PatientUpdateTest(APITestCase):
    @parameterized.expand([
        # ('patient_code', 'code', 'A00187654321', 'A00187654321'),  TODO serializer에서 unique한 code를 거르는것같음
        ('nickname', 'nickname', 'test', 'test'),
        ('treatment_started_date', 'treatment_started_date', timezone.now().today().strftime('%Y-%m-%d'),
         timezone.now().today().date()),
        ('additionally_detected_flag', 'additionally_detected_flag', 'true', True),
        ('additionally_detected_date', 'additionally_detected_date', timezone.now().today().strftime('%Y-%m-%d'),
         timezone.now().today().date()),
        ('discharged_flag', 'discharged_flag', 'true', True),
        ('registered_flag', 'registered_flag', 'true', True),
        ('medication_manage_flag', 'medication_manage_flag', 'true', True),
        ('daily_medication_count', 'daily_medication_count', '1회', 1),
        ('medication_noti_flag', 'medication_noti_flag', 'true', True),
        ('medication_noti_time_1', 'medication_noti_time_1', time_request_example_1am, datetime.time(1, 0)),
        ('medication_noti_time_2', 'medication_noti_time_2', time_request_example_1am, datetime.time(1, 0)),
        ('medication_noti_time_3', 'medication_noti_time_3', time_request_example_1am, datetime.time(1, 0)),
        ('medication_noti_time_4', 'medication_noti_time_4', time_request_example_1am, datetime.time(1, 0)),
        ('medication_noti_time_5', 'medication_noti_time_5', time_request_example_1am, datetime.time(1, 0)),
        ('visit_manage_flag', 'visit_manage_flag', 'true', True),
        ('next_visiting_date_time', 'next_visiting_date_time',
         date_time_request_example, datetime.datetime(2019, 11, 1, 15, 00, 00).astimezone()),
        ('visit_notification_flag', 'visit_notification_flag', 'true', True),
        ('visit_notification_before', 'visit_notification_before', 3600, 3600),
        ('health_manage_flag', 'health_manage_flag', 'true', True),
        ('daily_measurement_count', 'daily_measurement_count', '1회', 1),
        ('measurement_noti_flag', 'measurement_noti_flag', 'true', True),
        ('measurement_noti_time_1', 'measurement_noti_time_1', time_request_example_1am, datetime.time(1, 0)),
        ('measurement_noti_time_2', 'measurement_noti_time_2', time_request_example_1am, datetime.time(1, 0)),
        ('measurement_noti_time_3', 'measurement_noti_time_3', time_request_example_1am, datetime.time(1, 0)),
        ('measurement_noti_time_4', 'measurement_noti_time_4', time_request_example_1am, datetime.time(1, 0)),
        ('measurement_noti_time_5', 'measurement_noti_time_5', time_request_example_1am, datetime.time(1, 0))
    ])
    def test_update_success(self, request_param, field_name, value, value_db):
        """
        test api.views.PatientUpdate
        """
        url = reverse('patient-update')
        p = Patient.objects.create(code='A00112345678', kakao_user_id='abc123')
        data = {
            'userRequest': {'user': {'id': 'abc123'}},
            'action': {'params': {request_param: value}}
        }
        response = self.client.post(url, data, format='json')
        p.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(getattr(p, field_name), value_db)

    def test_update_success_when_test_true(self):
        """
        update patient when request.queryparams's test value is true.
        It results not actually saving it, but it will respond with serializer's data
        """
        field, value = ('nickname', 'test')
        url = reverse('patient-update')
        p = Patient.objects.create(code='A00112345678', kakao_user_id='abc123')
        original_data = getattr(p, field)
        data = {
            'userRequest': {'user': {'id': 'abc123'}},
            'action': {'params': {field: value}}
        }
        response = self.client.post(url + '?test=true', data, format='json')
        p.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(getattr(p, field), original_data)


class ValidateTest(APITestCase):
    def test_patient_code_success(self):
        """
        test for ValidatePatientCode
        P00012345 - 9 characters code
        * expect upper case
        """
        url = reverse('validate-patient-code')
        data = {
            'value': {'origin': 'p12312345678입니다'}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'P12312345678')

    def test_invalid_patient_code_fail(self):
        """
        test for ValidatePatientCode
        P00012345678 - 12 characters code
        """
        url = reverse('validate-patient-code')
        data = {
            'value': {'origin': 'P123'}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_patient_code_fail(self):
        """
        test for ValidatePatientCode
        expect fail. expect return 400 when requested duplicated patient code. (unique test)
        """
        Patient.objects.create(code='P12312345678', kakao_user_id='asd123')

        url = reverse('validate-patient-code')
        data = {
            'value': {'origin': 'P12312345678입니다'}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @parameterized.expand([
        ('1일 전', 86400),
        ('하루 전', 86400),
        ('이틀 전', 86400 * 2),
        ('1시간 전', 60 * 60),
        ('1시간 30분전', 60 * 60 * 1.5),
        ('5분전', 60 * 5),
    ])
    def test_time_before_success(self, request, response_value):
        """
        test for ValidateTimeBefore
        """
        p = Patient.objects.create(code='P12312345678', kakao_user_id='asd123')

        url = reverse('validate-time-before')
        data = {
            'value': {'origin': request}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], response_value)


class PatientMedicationNotiTest(APITestCase):
    # TODO 시간대 설정 성공/실패 테스트

    def test_medication_noti_reset(self):
        p = Patient.objects.create(code='P12312345678', kakao_user_id='asd123')
        p.daily_medication_count = 5
        p.medication_noti_flag = True
        p.medication_noti_time_1 = datetime.datetime.now()
        p.medication_noti_time_2 = datetime.datetime.now()
        p.medication_noti_time_3 = datetime.datetime.now()
        p.medication_noti_time_4 = datetime.datetime.now()
        p.medication_noti_time_5 = datetime.datetime.now()
        p.save()

        url = reverse('patient-medication-noti-reset')
        data = {
            'userRequest': {'user': {'id': 'asd123'}},
        }
        response = self.client.post(url, data, format='json')
        p.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(p.medication_noti_flag, None)
        self.assertEqual(p.daily_medication_count, 0)
        self.assertEqual(p.medication_noti_time_1, None)
        self.assertEqual(p.medication_noti_time_2, None)
        self.assertEqual(p.medication_noti_time_3, None)
        self.assertEqual(p.medication_noti_time_4, None)
        self.assertEqual(p.medication_noti_time_5, None)
        self.assertEqual(p.medication_noti_time_list(), list())
        self.assertEqual(p.has_undefined_noti_time(), False)
