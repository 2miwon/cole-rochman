from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Patient


class TempTest(APITestCase):
    def test_temp_patient_destroy_success(self):
        Patient.objects.create(code='PATIENT_CODE', kakao_user_id='abc123')
        self.assertEqual(Patient.objects.count(), 1)
        data = {
            'userRequest': {'user': {'id': 'abc123'}},
        }
        url = reverse('temp-patient-destroy')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Patient.objects.count(), 0)

    def test_temp_patient_destroy_fail(self):
        Patient.objects.create(code='PATIENT_CODE', kakao_user_id='abc123')
        self.assertEqual(Patient.objects.count(), 1)
        data = {
            'userRequest': {'user': {'id': 'unknown-kakao-id'}},
        }
        url = reverse('temp-patient-destroy')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Patient.objects.count(), 1)
