from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Patient


class PatientTest(APITestCase):
    def test_create(self):
        """
        create post
        """
        url = reverse('patient-create')
        data = {
            'userRequest': {'user': {'id': 123}},
            'action': {'detailParams': {'patient_code': {'value': 'test'}}}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(Patient.objects.get().code, 'test')
        self.assertEqual(Patient.objects.get().kakao_user_id, 123)
