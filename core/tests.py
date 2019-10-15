import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from parameterized import parameterized
from django.utils import timezone

from .models import Patient, Test


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
        create patient when request.data's test value is true.
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
        ('patient_code', 'code', 'A00187654321', 'A00187654321'),
        ('nickname', 'nickname', 'test', 'test'),
        ('treatment_started_date', 'treatment_started_date', timezone.now().today().strftime('%Y-%m-%d'),
         timezone.now().today().date()),
        ('additionally_detected_flag', 'additionally_detected_flag', 'true', True),
        ('additionally_detected_date', 'additionally_detected_date', timezone.now().today().strftime('%Y-%m-%d'),
         timezone.now().today().date()),
        ('discharged_flag', 'discharged_flag', 'true', True),
        ('registered_flag', 'registered_flag', 'true', True),
        ('medication_manage_flag', 'medication_manage_flag', 'true', True),
        ('daily_medication_count', 'daily_medication_count', 1, 1),
        ('medication_noti_flag', 'medication_noti_flag', 'true', True),
        ('medication_noti_time_1', 'medication_noti_time_1', '11:00', datetime.time(11, 0)),
        ('medication_noti_time_2', 'medication_noti_time_2', '11:00', datetime.time(11, 0)),
        ('medication_noti_time_3', 'medication_noti_time_3', '11:00', datetime.time(11, 0)),
        ('medication_noti_time_4', 'medication_noti_time_4', '11:00', datetime.time(11, 0)),
        ('medication_noti_time_5', 'medication_noti_time_5', '11:00', datetime.time(11, 0)),
        ('visit_manage_flag', 'visit_manage_flag', 'true', True),
        ('next_visiting_date', 'next_visiting_date', timezone.now().today().strftime('%Y-%m-%d'),
         timezone.now().today().date()),
        ('visit_notification_flag', 'visit_notification_flag', 'true', True),
        ('visit_notification_time', 'visit_notification_time', '11:00', datetime.time(11, 0)),
        ('health_manage_flag', 'health_manage_flag', 'true', True),
        ('daily_measurement_count', 'daily_measurement_count', 1, 1),
        ('measurement_noti_flag', 'measurement_noti_flag', 'true', True),
        ('measurement_noti_time_1', 'measurement_noti_time_1', '11:00', datetime.time(11, 0)),
        ('measurement_noti_time_2', 'measurement_noti_time_2', '11:00', datetime.time(11, 0)),
        ('measurement_noti_time_3', 'measurement_noti_time_3', '11:00', datetime.time(11, 0)),
        ('measurement_noti_time_4', 'measurement_noti_time_4', '11:00', datetime.time(11, 0)),
        ('measurement_noti_time_5', 'measurement_noti_time_5', '11:00', datetime.time(11, 0))
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
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(getattr(p, field_name), value_db)


class ValidateTest(APITestCase):
    def test_patient_code_success(self):
        """
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
        fail. expect return 400 when requested duplicated patient code. (unique test)
        """
        Patient.objects.create(code='P12312345678', kakao_user_id='asd123')

        url = reverse('validate-patient-code')
        data = {
            'value': {'origin': 'P12312345678입니다'}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestTest(APITestCase):
    def test_create(self):
        """
        create post
        """
        url = reverse('test')
        data = {
            'userRequest': {'user': {'id': 123}},
            'action': {'detailParams': {'patient_code': {'value': 'test'}}}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Test.objects.count(), 1)
