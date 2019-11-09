from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Patient
from core.tests.helper.helper import get_first_simple_text, message_in_response


class HealthManangementEntranceTest(APITestCase):
    def test_health_management_entrance_first(self):
        """
        산소포화도 관리 첫 시작 단계 진입
        """
        Patient.objects.create(code='P12312345678', kakao_user_id='asd123')
        url = reverse('patient-health-entrance')
        data = {
            'userRequest': {'user': {'id': 'asd123'}},
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('산소포화도 관리를 시작하시겠습니까?', message_in_response(response))

    def test_health_management_entrance_reset(self):
        """
        산소포화도 관리 재설정 단계 진입
        """
        Patient.objects.create(code='P12312345678', kakao_user_id='asd123', health_manage_flag=True)
        url = reverse('patient-health-entrance')
        data = {
            'userRequest': {'user': {'id': 'asd123'}},
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('산소포화도 관리를 설정한 적이 있습니다. 다시 설정할까요?', message_in_response(response))

    def test_health_management_entrance_fail_404(self):
        """
        Exception for 404 not found
        """
        url = reverse('patient-health-entrance')
        data = {
            'userRequest': {'user': {'id': 'unknown-user-id'}},
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # TODO mock.patch
        # with patch('core.api.views.health.HealthManangementEntrance.build_response_fallback_404'
        #            ) as build_response_fallback_404:
        #     build_response_fallback_404.assert_called()
        self.assertEqual(get_first_simple_text(response), '계정을 먼저 등록해주셔야 해요. 계정을 등록하러 가볼까요?')
