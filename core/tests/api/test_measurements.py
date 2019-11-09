from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Patient
from core.tests.helper.helper import message_in_response


class MeasurementResultCreateTest(APITestCase):
    def test_success(self):
        Patient.objects.create(code='A00112345678', kakao_user_id='abc123')
        url = reverse('patient-measurement-create')
        data = {
            'userRequest': {'user': {'id': 'abc123'}},
            'action': {
                'params': {'oxygen_saturation': 60}
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fail_404_when_no_param(self):
        Patient.objects.create(code='A00112345678', kakao_user_id='abc123')
        url = reverse('patient-measurement-create')
        data = {
            'userRequest': {'user': {'id': 'abc123'}},
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('알 수 없는 오류가 발생하였습니다', message_in_response(response))
