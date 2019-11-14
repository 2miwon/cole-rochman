from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from parameterized import parameterized

from core.models import Patient, Hospital


class ValidateTest(APITestCase):
    def test_patient_nickname_success(self):
        """
        test for ValidatePatientNickname
        P00012345 - 9 characters code
        * expect upper case
        """
        url = reverse('validate-patient-nickname')
        data = {
            'value': {'origin': '테스트별명'}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], '테스트별명')

    def test_patient_nickname_fail(self):
        """
        test for ValidatePatientNickname
        P00012345 - 9 characters code
        * expect upper case
        """
        url = reverse('validate-patient-nickname')
        data = {
            'value': {'origin': ''}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_hospital_code_success_number(self):
        """
        test for ValidateHospitalCode success
        001 - 3 characters code
        """
        Hospital.objects.create(code='A001', name='test')

        url = reverse('validate-hospital-code')
        data = {
            'value': {'origin': 'A001'}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'A001')

    def test_hospital_code_fail_not_found(self):
        """
        fail when hospital code not exists
        001 - 3 characters code
        """
        Hospital.objects.create(code='A001', name='test')

        url = reverse('validate-hospital-code')
        data = {
            'value': {'origin': 'A002'}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], '알 수 없는 병원 코드입니다. 다시 한 번 확인해주세요.')

    def test_hospital_code_fail_invalid_request(self):
        """
        fail when hospital code not exists
        001 - 3 characters code
        """
        Hospital.objects.create(code='A001', name='test')

        url = reverse('validate-hospital-code')
        data = {
            'value': {'origin': ''}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patient_code_success(self):
        """
        test for ValidatePatientCode
        P00012345 - 9 characters code
        * expect upper case
        """
        Hospital.objects.create(code='A001', name='test')
        url = reverse('validate-patient-code')
        data = {
            'value': {'origin': 'a00112345678입니다'}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'SUCCESS')
        self.assertEqual(response.data['value'], 'A00112345678')

    def test_invalid_patient_code_fail(self):
        """
        test for ValidatePatientCode
        A00112345678 - 12 characters code
        """
        url = reverse('validate-patient-code')
        data = {
            'value': {'origin': 'P123'}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'FAIL')

    def test_invalid_patient_code_fail_invalid_hospital_code(self):
        """
        test for ValidatePatientCode
        A00112345678 - 12 characters code
        A001 -> hospital_code
        """
        url = reverse('validate-patient-code')
        data = {
            'value': {'origin': 'A00212345678'}  # unknown Hospital code
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'FAIL')

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

    def test_measurement_result_oxygen_saturation_success(self):
        """
        test for ValidateMeasurementResultOxygenSaturation
        """
        url = reverse('validate-measurement-result-oxygen-saturation')
        data = {
            'value': {'origin': "12"}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 12)
