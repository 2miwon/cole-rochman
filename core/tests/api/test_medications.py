import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Patient


class PatientMedicationNotiTest(APITestCase):
    # TODO 시간대 설정 성공/실패 테스트

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

        url = reverse('patient-medication-noti-reset')
        data = {
            'userRequest': {'user': {'id': 'asd123'}},
        }
        response = self.client.post(url, data, format='json')
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
