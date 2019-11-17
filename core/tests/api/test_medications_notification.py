import json

from django.http import Http404
from django.http.request import HttpRequest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Patient


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
