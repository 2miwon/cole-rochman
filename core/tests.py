from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Patient, Test


class PatientTest(APITestCase):
    def test_create_success(self):
        """
        create patient
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

    def test_create_success_when_test_true(self):
        """
        create patient when request.data's test value is true.
        It results not actually saving it, but it will respond with serializer's data
        """
        url = reverse('patient-create')
        data = {
            'userRequest': {'user': {'id': 123}},
            'action': {'detailParams': {'patient_code': {'value': 'test'}}}
        }

        response = self.client.post(url + '?test=true', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 0)


class ValidateTest(APITestCase):
    def test_patient_code_success(self):
        """
        P00012345 - 9 characters code
        """
        url = reverse('validate-patient-code')
        data = {
            'value': {'origin': 'P12345678'}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patient_code_fail(self):
        """
        P00012345 - 9 characters code
        """
        url = reverse('validate-patient-code')
        data = {
            'value': {'origin': 'P0000125'}
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
