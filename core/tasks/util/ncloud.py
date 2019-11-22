import base64
import hashlib
import hmac
import time

from django.conf import settings


class NcloudRequest:
    '''
    POST https://sens.apigw.ntruss.com/alimtalk/v2/services/{serviceId}/messages

    Content-Type: application/json; charset=utf-8
    x-ncp-apigw-timestamp: {Timestamp}
    x-ncp-iam-access-key: {Sub Account Access Key}
    x-ncp-apigw-signature-v2: {API Gateway Signature}
    '''

    method = 'POST'
    uri = 'https://sens.apigw.ntruss.com/sms/v2/services/ncp:sms:kr:257307776620:cole-rochman/messages'

    access_key = settings.NCLOUD['ACCESS_KEY']
    secret_key = settings.NCLOUD['SECRET_KEY']

    def build_headers(self) -> dict:
        headers = {
            'content-type': 'application/json; charset=utf-8',
            'x-ncp-apigw-timestamp': self.make_timestamp(),
            'x-ncp-iam-access-key': self.access_key,
            'x-ncp-apigw-signature-v2': self.make_signature()
        }
        return headers

    @staticmethod
    def make_timestamp():
        timestamp = int(time.time() * 1000)
        timestamp = str(timestamp)

        return timestamp

    def make_signature(self):
        if self.method not in ['GET', 'POST']:
            raise ValueError('method has to be one of [GET, POST]')

        timestamp = self.make_timestamp()
        secret_key = bytes(self.secret_key, 'UTF-8')

        message = self.method + " " + self.uri + "\n" + timestamp + "\n" + self.access_key
        message = bytes(message, 'UTF-8')

        signing_key = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
        return signing_key
