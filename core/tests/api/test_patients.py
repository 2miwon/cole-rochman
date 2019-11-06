import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from parameterized import parameterized
from django.utils import timezone

from core.models import Patient, Hospital

time_request_example_1am = '{"timeHeadword": "am", "hour": "1", "second": null, "timeTag": "am", "time": "01:00:00", "date": "2019-10-16", "minute": null}'
date_time_request_example = '{"dateTag": null, "timeHeadword": "pm", "hour": null, "dateHeadword": null, "time": "15:00:00",\
          "second": null, "month": "11", "timeTag": "pm", "year": null, "date": "2019-11-01", "day": "1", "minute": null}'


def get_first_simple_text(response):
    return response.data['template']['outputs'][0]['simpleText']['text']


class PatientCreateTest(APITestCase):
    def test_create_start_success_already_exist(self):
        """
        patient create start. expects different responses by the existence of user.
        """
        url = reverse('patient-create-start')
        data = {
            'userRequest': {'user': {'id': 'unknown-id'}},
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('계정을 등록하시겠습니까?' in get_first_simple_text(response), True)

    def test_create_start_success_not_exist(self):
        """
        patient create start. expects different responses by the existence of user.
        """
        Patient.objects.create(code='A00112345678', kakao_user_id='abc123')
        url = reverse('patient-create-start')
        data = {
            'userRequest': {'user': {'id': 'abc123'}},
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('이미 계정이 등록되어 있습니다' in get_first_simple_text(response), True)

    def test_create_success(self):
        """
        create patient
        """
        h = Hospital.objects.create(code='A001', name='seobuk')
        url = reverse('patient-create')
        data = {
            'userRequest': {'user': {'id': 'asd123'}},
            'action': {
                'detailParams': {
                    'patient_code': {'value': 'A00112345678'},
                    'nickname': {'value': '별님'}
                }
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(Patient.objects.first().code, 'A00112345678')
        self.assertEqual(Patient.objects.first().hospital, h)
        self.assertEqual(Patient.objects.first().nickname, '별님')
        self.assertEqual(Patient.objects.first().kakao_user_id, 'asd123')

    def test_create_success_when_test_true(self):
        """
        create patient when request.queryparams's test value is true.
        It results not actually saving it, but it will respond with serializer's data
        """
        h = Hospital.objects.create(code='A001', name='seobuk')
        url = reverse('patient-create')
        data = {
            'userRequest': {'user': {'id': 'asd123'}},
            'action': {
                'detailParams': {
                    'patient_code': {'value': 'T00112345678'},
                    'hospital_code': {'value': 'A001'},
                    'nickname': {'value': '별님'}
                }
            }
        }

        response = self.client.post(url + '?test=true', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        ('register_completed_flag', 'register_completed_flag', 'true', True),
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
        if 'date' in request_param and 'date_time' not in request_param:
            data = {
                'userRequest': {'user': {'id': 'abc123'}},
                'action': {'params': {request_param: {'value': value}}}
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
