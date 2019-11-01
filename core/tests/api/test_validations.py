from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from parameterized import parameterized

from core.models import Patient


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
