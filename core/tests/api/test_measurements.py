import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Patient
from core.tests.helper.helper import message_in_response


class PatientMeasurementEntranceTest(APITestCase):
    url = reverse('patient-measurement-entrance')

    def test_health_management_entrance_first(self):
        """
        산소포화도 관리 첫 시작 단계 진입
        """
        Patient.objects.create(code='P12312345678', kakao_user_id='asd123')

        data = {
            'userRequest': {'user': {'id': 'asd123'}},
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('산소포화도 관리를 시작하시겠습니까?', message_in_response(response))

    def test_health_management_entrance_reset(self):
        """
        산소포화도 관리 재설정 단계 진입
        """
        Patient.objects.create(code='P12312345678', kakao_user_id='asd123', measurement_manage_flag=True)
        data = {
            'userRequest': {'user': {'id': 'asd123'}},
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('산소포화도 관리를 설정한 적이 있습니다. 다시 설정할까요?', message_in_response(response))

    def test_health_management_entrance_fail_404(self):
        """
        Exception for 404 not found
        """
        url = reverse('patient-measurement-entrance')
        data = {
            'userRequest': {'user': {'id': 'unknown-user-id'}},
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # TODO mock.patch
        # with patch('core.api.views.health.PatientMeasurementEntrance.build_response_fallback_404'
        #            ) as build_response_fallback_404:
        #     build_response_fallback_404.assert_called()
        self.assertIn('계정을 먼저 등록해주셔야 해요. 계정을 등록하러 가볼까요?', message_in_response(response))


class PatientMeasurementNotiTimeQuestionTest(APITestCase):
    url = reverse('patient-measurement-noti-time-question-start')

    def test_success_for_question(self):
        """
        회차가 남아있는 경우
        """
        Patient.objects.create(code='A00112345678', kakao_user_id='abc123', measurement_manage_flag=True,
                               daily_measurement_count=3)
        data = {
            'userRequest': {'user': {'id': 'abc123'}},
            'action': {
                'params': {'noti_time': {'value': '10:00:00', 'userTimeZone': 'UTC+9'}}
            }
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('1회차 산소포화도 확인 알림을 설정할까요', message_in_response(response))

    def test_success_for_complete(self):
        """
        회차가 남아있지 않은 경우
        """
        Patient.objects.create(code='A00112345678', kakao_user_id='abc123', measurement_noti_flag=True,
                               daily_measurement_count=1,
                               measurement_noti_time_1=datetime.datetime(2019, 11, 1, 15, 00, 00).astimezone())
        data = {
            'userRequest': {'user': {'id': 'abc123'}},
            'action': {
                'params': {'noti_time': {'value': '10:00:00', 'userTimeZone': 'UTC+9'}}
            }
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('이미 모든 회차 알림 설정을 마쳤습니다.', message_in_response(response))

    def test_fail_404(self):
        """
                Exception for 404 not found
                """
        data = {
            'userRequest': {'user': {'id': 'unknown-user-id'}},
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('계정을 먼저 등록해주셔야 해요. 계정을 등록하러 가볼까요?', message_in_response(response))


class MeasurementResultCreateTest(APITestCase):
    url = reverse('patient-measurement-create')

    def test_success(self):
        Patient.objects.create(code='A00112345678', kakao_user_id='abc123')

        data = {
            'userRequest': {'user': {'id': 'abc123'}},
            'action': {
                'params': {'oxygen_saturation': 60}
            }
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fail_404_when_no_param(self):
        Patient.objects.create(code='A00112345678', kakao_user_id='abc123')
        data = {
            'userRequest': {'user': {'id': 'abc123'}},
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('알 수 없는 오류가 발생하였습니다', message_in_response(response))
