import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Patient
from core.tests.helper.helper import get_first_simple_text, get_context


class PatientMedicationStartTest(APITestCase):
    url = reverse('patient-medication-start')

    def test_medication_start_success(self):
        p = Patient.objects.create(code='P12312345678', kakao_user_id='asd123')

        data = {
            'userRequest': {'user': {'id': 'asd123'}},
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_first_simple_text(response), '안녕하세요 콜로크만입니다.\n저와 함께 복약 관리를 시작하시겠습니까?')

    def test_medication_start_success_when_already_set(self):
        """
        Test successful response when medication_manage_flag is True
        """
        p = Patient.objects.create(code='P12312345678', kakao_user_id='asd123', medication_manage_flag=True)
        data = {
            'userRequest': {'user': {'id': 'asd123'}},
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('지난 번, 복약 관리를 설정한 적이 있습니다', get_first_simple_text(response))

    def test_medication_start_fail(self):
        data = {
            'userRequest': {'user': {'id': 'asd123'}},  # unknown user
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # with patch('core.api.views.medications.PatientMedicationEntrance.build_response_fallback_404'
        #            ) as build_response_fallback_404:
        #     build_response_fallback_404.assert_called()
        self.assertEqual(get_first_simple_text(response), '계정을 먼저 등록해주셔야 해요. 계정을 등록하러 가볼까요?')


# TODO 시간대 설정 성공/실패 테스트

class PatientMedicationNotiResetTest(APITestCase):
    url = reverse('patient-medication-noti-reset')

    def test_medication_noti_reset(self):
        p = Patient.objects.create(code='P12312345678', kakao_user_id='asd123')
        p.daily_medication_count = 5
        p.medication_noti_flag = True
        p.medication_noti_time_1 = datetime.datetime.now()
        p.medication_noti_time_2 = datetime.datetime.now()
        p.medication_noti_time_3 = datetime.datetime.now()
        p.medication_noti_time_4 = datetime.datetime.now()
        p.medication_noti_time_5 = datetime.datetime.now()
        p.save()

        data = {
            'userRequest': {'user': {'id': 'asd123'}},
        }

        response = self.client.post(self.url, data, format='json')
        p.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(p.medication_noti_flag, None)
        self.assertEqual(p.daily_medication_count, 0)
        self.assertEqual(p.medication_noti_time_1, None)
        self.assertEqual(p.medication_noti_time_2, None)
        self.assertEqual(p.medication_noti_time_3, None)
        self.assertEqual(p.medication_noti_time_4, None)
        self.assertEqual(p.medication_noti_time_5, None)
        self.assertEqual(p.medication_noti_time_list(), list())
        self.assertEqual(p.need_medication_noti_time_set(), False)


class PatientMedicationRestartTest(APITestCase):
    url = reverse('patient-medication-restart')

    def test_medication_restart_success(self):
        """
        Expect successful response for the request to PatientMedicationRestart()
        when p.medication_manage_flag = True
        """
        p = Patient.objects.create(code='P12312345678', kakao_user_id='asd123', medication_manage_flag=True,
                                   daily_medication_count=3)
        data = {
            'userRequest': {'user': {'id': 'asd123'}},
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('지난 번, 복약 관리를 설정한 적이 있습니다.' in get_first_simple_text(response), True)
        self.assertEqual(get_context(response)[0]['params']['daily_medication_count'], 3)

    def test_medication_restart_fail_when_no_patient(self):
        """
        Expect failed response with message of fail
        when patient does not exist.
        """

        data = {
            'userRequest': {'user': {'id': 'asd123'}},
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('계정을 먼저 등록해주셔야 해요' in get_first_simple_text(response), True)

    def test_medication_restart_fail_when_not_set_medication_manage(self):
        """
        Expect failed response with fail message
        when patient.manage_medication_flag is not True
        """
        p = Patient.objects.create(code='P12312345678', kakao_user_id='asd123')
        data = {
            'userRequest': {'user': {'id': 'asd123'}},
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('설정된 복약 관리가 없습니다' in get_first_simple_text(response), True)
