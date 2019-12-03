import datetime
from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Patient
from core.tests.helper.helper import message_in_response


class MeasurementResultCheckTest(APITestCase):
    url = reverse('patient-measurement-create')
    data = {
        'userRequest': {'user': {'id': 'asd123'}},
        'action': {
            "params":
                {"oxygen_saturation": 90}
        }
    }

    @mock.patch('core.api.views.measurements_notification.get_now', mock.MagicMock(return_value=datetime.time(hour=9)))
    def test_success(self):
        p = Patient.objects.create(
            code='P12312345678', kakao_user_id='asd123', measurement_manage_flag=True, daily_measurement_count=3,
            measurement_noti_flag=True, measurement_noti_time_1=datetime.time(hour=8),
            measurement_noti_time_2=datetime.time(hour=10), measurement_noti_time_3=datetime.time(hour=12),
        )

        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(p.measurement_results.last().oxygen_saturation, 90)


class MeasurementResultCheckFromNotification(APITestCase):
    url = reverse('patient-measurement-check')
    data = {
        'userRequest': {'user': {'id': 'asd123'}},
        'action': {
            "params":
                {"oxygen_saturation": '{\\"amount\\": 90, \\"unit\\": null}'}
        }
    }

    @mock.patch('core.api.views.measurements_notification.get_now', mock.MagicMock(return_value=datetime.time(hour=9)))
    def test_success(self):
        p = Patient.objects.create(
            code='P12312345678', kakao_user_id='asd123', measurement_manage_flag=True, daily_measurement_count=3,
            measurement_noti_flag=True, measurement_noti_time_1=datetime.time(hour=8),
            measurement_noti_time_2=datetime.time(hour=10), measurement_noti_time_3=datetime.time(hour=12),
        )

        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(p.measurement_results.last().oxygen_saturation, 90)
