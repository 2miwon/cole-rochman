import datetime
from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Patient, MedicationResult
from core.tests.helper.helper import message_in_response


class PastMedicationCheckChooseTimeTest(APITestCase):
    url = reverse('patients-medication-past-check-choose-time')
    data = {
        'userRequest': {'user': {'id': 'asd123'}},
        'action': {
            "detailParams":
                {"medication_date":
                    {
                        "origin": "2019-11-18",
                        "value": '{"value":"2019-11-18","userTimeZone":"UTC+9"}'
                    }
                }
        }
    }

    def test_success(self):
        Patient.objects.create(code='P12312345678', kakao_user_id='asd123', medication_manage_flag=True,
                               daily_medication_count=3)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i, d in enumerate(response.data['template']['quickReplies']):
            self.assertEqual(d.get('label'), '%s회' % (i + 1))


class PastMedicationEntranceTest(APITestCase):
    url = reverse('patients-medication-past-entrance')
    data = {
        'userRequest': {'user': {'id': 'asd123'}},
    }

    @mock.patch('core.api.views.medications_notification.get_now', mock.MagicMock(return_value=datetime.time(hour=9)))
    def test_success(self):
        p = Patient.objects.create(
            code='P12312345678', kakao_user_id='asd123', medication_manage_flag=True, daily_medication_count=3,
            medication_noti_flag=True, medication_noti_time_1=datetime.time(hour=8),
            medication_noti_time_2=datetime.time(hour=10), medication_noti_time_3=datetime.time(hour=12),
        )
        response = self.client.post(self.url, self.data, format='json')
        p.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('지난 복약 상태를 변경하시겠어요', message_in_response(response))

    @mock.patch('core.api.views.medications_notification.get_now', mock.MagicMock(return_value=datetime.time(hour=9)))
    def test_fail_when_patient_didnt_set_noti_time(self):
        p = Patient.objects.create(
            code='P12312345678', kakao_user_id='asd123', medication_manage_flag=True, daily_medication_count=3,
            medication_noti_flag=True
        )
        response = self.client.post(self.url, self.data, format='json')
        p.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('설정된 복약 알림이 없습니다', message_in_response(response))


class PastMedicationSuccessTest(APITestCase):
    url = reverse('patients-medication-past-check-success')
    data = {
        'userRequest': {'user': {'id': 'asd123'}},
    }

    @mock.patch('core.api.views.medications_notification.get_now', mock.MagicMock(return_value=datetime.time(hour=9)))
    def test_success(self):
        p = Patient.objects.create(
            code='P12312345678', kakao_user_id='asd123', medication_manage_flag=True, daily_medication_count=3,
            medication_noti_flag=True, medication_noti_time_1=datetime.time(hour=8),
            medication_noti_time_2=datetime.time(hour=10), medication_noti_time_3=datetime.time(hour=12),
        )
        response = self.client.post(self.url, self.data, format='json')
        p.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(p.medication_results.last().get_status(), MedicationResult.STATUS.SUCCESS.value)
        self.assertEqual(p.medication_results.last().medication_time_num, 1)
        self.assertEqual(p.medication_results.last().medication_time, datetime.time(hour=8))

    @mock.patch('core.api.views.medications_notification.get_now', mock.MagicMock(return_value=datetime.time(hour=9)))
    def test_fail_when_patient_didnt_set_noti_time(self):
        p = Patient.objects.create(
            code='P12312345678', kakao_user_id='asd123', medication_manage_flag=True, daily_medication_count=3,
            medication_noti_flag=True
        )
        response = self.client.post(self.url, self.data, format='json')
        p.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('설정된 복약 알림이 없습니다', message_in_response(response))


class PastMedicationFailedTest(APITestCase):
    url = reverse('patients-medication-past-check-failed')
    data = {
        'userRequest': {'user': {'id': 'asd123'}},
    }

    @mock.patch('core.api.views.medications_notification.get_now', mock.MagicMock(return_value=datetime.time(hour=9)))
    def test_success(self):
        p = Patient.objects.create(
            code='P12312345678', kakao_user_id='asd123', medication_manage_flag=True, daily_medication_count=3,
            medication_noti_flag=True, medication_noti_time_1=datetime.time(hour=8),
            medication_noti_time_2=datetime.time(hour=10), medication_noti_time_3=datetime.time(hour=12),
        )
        response = self.client.post(self.url, self.data, format='json')
        p.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(p.medication_results.last().get_status(), MedicationResult.STATUS.FAILED.value)
        self.assertEqual(p.medication_results.last().medication_time_num, 1)
        self.assertEqual(p.medication_results.last().medication_time, datetime.time(hour=8))
        self.assertIn('다음 회차에는 꼭 복약하셔야합니다. ', message_in_response(response))


class PastMedicationSideEffectTest(APITestCase):
    url = reverse('patients-medication-past-check-side-effect')
    data = {
        'userRequest': {'user': {'id': 'asd123'}},
        'action': {
            "detailParams":
                {
                    "status_info": {"origin": "위장장애(속쓰림)", "value": "위장장애(속쓰림)"},
                    "severity": {"origin": 1, "value": 1}
                }
        }
    }

    @mock.patch('core.api.views.medications_notification.get_now', mock.MagicMock(return_value=datetime.time(hour=9)))
    def test_success(self):
        p = Patient.objects.create(
            code='P12312345678', kakao_user_id='asd123', medication_manage_flag=True, daily_medication_count=3,
            medication_noti_flag=True, medication_noti_time_1=datetime.time(hour=8),
            medication_noti_time_2=datetime.time(hour=10), medication_noti_time_3=datetime.time(hour=12),
        )
        response = self.client.post(self.url, self.data, format='json')
        p.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(p.medication_results.last().get_status(), MedicationResult.STATUS.SIDE_EFFECT.value)
        self.assertEqual(p.medication_results.last().medication_time_num, 1)
        self.assertEqual(p.medication_results.last().status_info, '위장장애(속쓰림)')
        self.assertEqual(p.medication_results.last().severity, 1)
        self.assertEqual(p.medication_results.last().medication_time, datetime.time(hour=8))
        self.assertIn('알려주셔서 감사합니다.', message_in_response(response))
