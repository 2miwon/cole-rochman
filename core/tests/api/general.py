from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ResponseAlwaysOkTest(APITestCase):
    def test_success(self):
        url = reverse('general-response-always-ok')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
