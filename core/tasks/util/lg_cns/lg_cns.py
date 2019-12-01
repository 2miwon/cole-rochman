import requests
from django.conf import settings

from core.tasks.util.lg_cns.error_codes import get_error_desc


class Lgcns:
    method = 'POST'
    url = 'https://talkapi.lgcns.com/request/kakao.json'

    auth_token = settings.LGCNS.get('API_KEY')
    server_name = settings.LGCNS.get('CHANNEL_ID')
    payment_type = 'P'

    service_no = settings.LGCNS.get('SERVICE_NO')

    def build_headers(self):
        headers = {
            'authToken': self.auth_token,
            'serverName': self.server_name,
            'paymentType': self.payment_type,
            'Content-Type': 'application/json; charset=UTF-8'
        }
        return headers


class LgcnsRequest(Lgcns):
    def __init__(self, payload: dict):
        self.payload = payload
        self.headers = self.build_headers()
        self.body = self.build_body(payload)

    def build_body(self, payload: dict):
        body = {'service': self.service_no}
        body.update(payload)
        return body

    def send(self):
        import json
        response = requests.post(url=self.url, headers=self.headers, data=json.dumps(self.body))

        response_content = json.loads(response.content)
        description = get_error_desc(response_content.get('status'))
        response_content.update(description)

        return response.ok, response_content

# TODO (나중에)
# class LgcnsLookup(Lgcns):
