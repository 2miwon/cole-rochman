import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.api.util.helper import Kakao
from core.models import Patient


class PatientVisitStartTest(APITestCase):
    def test_success_discharged(self):
        p = Patient.objects.create(code='A00112345678', kakao_user_id='abc123', discharged_flag=True)
        url = reverse('patient-visit-start')
        data = {
            'userRequest': {'user': {'id': 'abc123'}},
            'action': {
                'params': {}
            }
        }
        response = self.client.post(url, data, format='json')
        p.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode().find('내원 관리를 시작하시겠습니까?') > 0, True)

    def test_success_not_discharged(self):
        p = Patient.objects.create(code='A00112345678', kakao_user_id='abc123', discharged_flag=False)
        url = reverse('patient-visit-start')
        data = {
            'userRequest': {'user': {'id': 'abc123'}},
            'action': {
                'params': {}
            }
        }
        response = self.client.post(url, data, format='json')
        p.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode().find('아직 퇴원을 하지 않으셔서 내원 관리를 하실 필요가 없어요.') > 0, True)

    def test_fail_404(self):
        url = reverse('patient-visit-start')
        data = {
            'userRequest': {'user': {'id': 'test_non_existing_user'}},
            'action': {
                'params': {}
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode().find('계정을 먼저 등록해주셔야 해요. 계정을 등록하러 가볼까요?') > 0, True)


class PatientVisitDateSetTest(APITestCase):
    def test_success(self):
        p = Patient.objects.create(code='A00112345678', kakao_user_id='abc123')
        url = reverse('patient-visit-date-set')
        data = {
            'userRequest': {'user': {'id': 'abc123'}},
            'action': {
                'params': {'next_visiting_date_time': "{\"value\":\"2018-03-20T10:15:00\",\"userTimeZone\":\"UTC+9\"}"}}
        }
        response = self.client.post(url, data, format='json')
        p.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(p.next_visiting_date_time,
                         datetime.datetime.strptime('2018-03-20T10:15:00', Kakao.DATETIME_FORMAT_STRING).astimezone())
        self.assertEqual(p.next_visiting_date_time_str(), '2018년 03월 20일 오전 10시 15분')


class PatientVisitTimeBeforeTest(APITestCase):
    def test_success(self):
        p = Patient.objects.create(code='A00112345678', kakao_user_id='abc123')
        url = reverse('patient-visit-noti-time')
        data = {
            'userRequest': {'user': {'id': 'abc123'}},
            'action': {'params': {'visit_notification_before': '12600'}}
        }
        response = self.client.post(url, data, format='json')
        p.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(getattr(p, 'visit_notification_before'), 12600)
        self.assertEqual(getattr(p, 'visit_notification_flag'), True)
