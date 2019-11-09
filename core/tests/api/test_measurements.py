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
    url = reverse('patient-measurement-noti-time-question')
    data = {
        'userRequest': {'user': {'id': 'abc123'}},
    }

    def test_success_for_question(self):
        """
        회차가 남아있는 경우
        """
        Patient.objects.create(code='A00112345678', kakao_user_id='abc123', measurement_manage_flag=True,
                               daily_measurement_count=3)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('1회차 산소포화도 확인 알림을 설정할까요', message_in_response(response))

    def test_success_for_complete(self):
        """
        회차가 남아있지 않은 경우
        """
        Patient.objects.create(code='A00112345678', kakao_user_id='abc123', measurement_noti_flag=True,
                               daily_measurement_count=1,
                               measurement_noti_time_1=datetime.datetime(2019, 11, 1, 15, 00, 00).astimezone())
        response = self.client.post(self.url, self.data, format='json')
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

    def test_restart_success(self):
        """
        url에 ?restart=true가 붙은 경우 다른 응답 내려주기
        """
        p = Patient.objects.create(code='A00112345678', kakao_user_id='abc123', measurement_noti_flag=True,
                                   daily_measurement_count=3,
                                   measurement_noti_time_1=datetime.datetime(2019, 11, 1, 15, 00, 00).astimezone())
        p.reset_measurement_noti_time()
        p.save()
        p.refresh_from_db()
        response = self.client.post(self.url + '?restart=true', self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('5dc709c38192ac0001c5d9cb', message_in_response(response))

    def test_restart_need_reset_time(self):
        """
        04-2 건강재설정_알림 설정 질문_시간대리셋필요
        5dc72164ffa74800014107b7

        detail_params에 reset_measurement_noti_time == true 인 경우. patient.reset_measurement_noti_time()
        """
        p = Patient.objects.create(code='A00112345678', kakao_user_id='abc123', measurement_noti_flag=True,
                                   daily_measurement_count=1,
                                   measurement_noti_time_1=datetime.datetime(2019, 11, 1, 15, 00, 00).astimezone())
        data = self.data.copy()
        data['action'] = {'detailParams': {'reset_measurement_noti_time': {'value': 'true'}}}
        response = self.client.post(self.url + '?restart=true', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('이미 모든 회차 알림 설정을 마쳤습니다', message_in_response(response))


class PatientMeasurementNotiSetTimeTest(APITestCase):
    url = reverse('patient-measurement-noti-set-time')
    data = {
        'userRequest': {'user': {'id': 'abc123'}},
        'action': {
            'params': {'noti_time': '{"value": "10:00:00", "userTimeZone": "UTC+9"}'}
        }
    }

    def test_success(self):
        """
        아직 회차 설정이 남은 경우
        """
        p = Patient.objects.create(code='A00112345678', kakao_user_id='abc123', measurement_noti_flag=True,
                                   daily_measurement_count=3,
                                   measurement_noti_time_1=datetime.datetime(2019, 11, 1, 15, 00, 00).astimezone())
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('10시 00분', message_in_response(response))
        self.assertIn('5dbfaeaf92690d0001e8805b', message_in_response(response))

    def test_success_complete(self):
        """
        모든 회차 설정이 끝난 경우
        """
        p = Patient.objects.create(code='A00112345678', kakao_user_id='abc123', measurement_noti_flag=True,
                                   daily_measurement_count=1,
                                   measurement_noti_time_1=datetime.datetime(2019, 11, 1, 15, 00, 00).astimezone())
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('모든 회차 알림 설정을 마쳤습니다', message_in_response(response))
        self.assertIn('5dbfb1ee8192ac00016aa32b', message_in_response(response))

    def test_success_restart(self):
        """
        아직 회차 설정이 남은 경우 + 재설정인 경우
        """
        p = Patient.objects.create(code='A00112345678', kakao_user_id='abc123', measurement_noti_flag=True,
                                   daily_measurement_count=3,
                                   measurement_noti_time_1=datetime.datetime(2019, 11, 1, 15, 00, 00).astimezone())
        response = self.client.post(self.url + '?restart=true', self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('10시 00분', message_in_response(response))
        self.assertIn('5dc7097affa74800014107ac', message_in_response(response))

    def test_success_complete_restart(self):
        """
        모든 회차 설정이 끝난 경우 + 재설정인 경우
        """
        p = Patient.objects.create(code='A00112345678', kakao_user_id='abc123', measurement_noti_flag=True,
                                   daily_measurement_count=1,
                                   measurement_noti_time_1=datetime.datetime(2019, 11, 1, 15, 00, 00).astimezone())
        response = self.client.post(self.url + '?restart=true', self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('모든 회차 알림 설정을 마쳤습니다', message_in_response(response))
        self.assertIn('5dc709d48192ac0001c5d9cd', message_in_response(response))


# class PatientMeasurementRestartTest(APITestCase):
#     url = reverse('patient-measurement-restart')
#     data = {
#         'userRequest': {'user': {'id': 'abc123'}},
#     }
#
#     def test_success(self):
#         Patient.objects.create(code='A00112345678', kakao_user_id='abc123', daily_measurement_count=3)
#
#         response = self.client.post(self.url, self.data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('산소포화도 관리를 설정한 적이 있습니다', message_in_response(response))
#         self.assertIn('"context":{"values":[{"name":"건강관리재설정","lifeSpan":5,"params":{"daily_measurement_count":3',
#                       message_in_response(response))
#
#     def test_reset_measurement(self):
#         p = Patient.objects.create(code='A00112345678', kakao_user_id='abc123', daily_measurement_count=3,
#                                    measurement_noti_time_1=datetime.datetime(2019, 11, 1, 15, 00, 00).astimezone())
#         url = reverse('patient-update')
#         data = self.data
#         data['action'] = {
#             'detailParams': {'reset_measurement_noti': {'value': 'true'}}
#         }
#         response = self.client.post(url, data, format='json')
#
#         p.refresh_from_db()
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(p.daily_measurement_count, 0)
#         self.assertEqual(p.measurement_noti_time_1, None)
#         self.assertEqual(p.measurement_noti_time_list(), [])
#         self.assertEqual(p.need_measurement_noti_time_set(), False)

class PatientMeasurementNotiResetTest(APITestCase):
    url = reverse('patient-measurement-noti-reset')
    data = {
        'userRequest': {'user': {'id': 'abc123'}},
    }

    def test_success(self):
        """
        리셋 성공
        """
        p = Patient.objects.create(code='A00112345678', kakao_user_id='abc123', measurement_manage_flag=True,
                                   measurement_noti_flag=True, daily_measurement_count=5,
                                   measurement_noti_time_1=datetime.datetime(2019, 11, 1, 15, 00, 00).astimezone(),
                                   measurement_noti_time_2=datetime.datetime(2019, 11, 1, 15, 00, 00).astimezone(),
                                   measurement_noti_time_3=datetime.datetime(2019, 11, 1, 15, 00, 00).astimezone(),
                                   measurement_noti_time_4=datetime.datetime(2019, 11, 1, 15, 00, 00).astimezone(),
                                   measurement_noti_time_5=datetime.datetime(2019, 11, 1, 15, 00, 00).astimezone(),
                                   )
        response = self.client.post(self.url, self.data, format='json')
        p.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(p.measurement_manage_flag, None)
        self.assertEqual(p.measurement_noti_flag, None)
        self.assertEqual(p.daily_measurement_count, 0)
        self.assertEqual(p.measurement_noti_time_1, None)
        self.assertEqual(p.measurement_noti_time_2, None)
        self.assertEqual(p.measurement_noti_time_3, None)
        self.assertEqual(p.measurement_noti_time_4, None)
        self.assertEqual(p.measurement_noti_time_5, None)


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
