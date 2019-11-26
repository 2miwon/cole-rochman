import base64
import hashlib
import hmac
import time

import requests
from django.conf import settings


class NcloudRequest:
    """
    Content-Type: application/json; charset=utf-8
    x-ncp-apigw-timestamp: {Timestamp}
    x-ncp-iam-access-key: {Sub Account Access Key}
    x-ncp-apigw-signature-v2: {API Gateway Signature}
    """

    method = ''
    uri = ''

    access_key = settings.NCLOUD['ACCESS_KEY']
    secret_key = settings.NCLOUD['SECRET_KEY']

    @staticmethod
    def _make_timestamp():
        timestamp = int(time.time() * 1000)
        timestamp = str(timestamp)

        return timestamp

    @staticmethod
    def get_exception(code):
        from core.tasks.util.ncloud.exceptions import get_exception
        return get_exception(code)

    def _make_signature(self, timestamp):
        if self.method not in ['GET', 'POST']:
            raise ValueError('method has to be one of [GET, POST]')

        secret_key = bytes(self.secret_key, 'UTF-8')

        message = self.method + " " + self.uri + "\n" + timestamp + "\n" + self.access_key
        message = bytes(message, 'UTF-8')

        signing_key = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
        return signing_key

    def build_headers(self) -> dict:
        timestamp = self._make_timestamp()
        headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'x-ncp-apigw-timestamp': timestamp,
            'x-ncp-iam-access-key': self.access_key,
            'x-ncp-apigw-signature-v2': self._make_signature(timestamp)
        }
        return headers


class NcloudRequestBizMessage(NcloudRequest):
    """
    POST https://sens.apigw.ntruss.com/alimtalk/v2/services/{serviceId}/messages
    """
    method = 'POST'
    uri = '/alimtalk/v2/services/{}/messages'.format(settings.BIZ_MESSAGE['SERVICE_ID'])
    url = 'https://sens.apigw.ntruss.com{}'.format(uri)

    def __init__(self, payload: dict):
        self.payload = payload

    def send(self):
        import json
        response = requests.post(url=self.url, headers=self.build_headers(), data=json.dumps(self.payload))
        return response.ok, json.loads(response.content)
