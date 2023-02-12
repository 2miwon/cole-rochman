import json

import requests
from django.conf import settings
from requests import Response
import random

from core.tasks.util.bizppurio.error_codes import get_error_desc

class Bizppurio:
    
    def build_headers(self):
        url_token = 'https://api.bizppurio.com/v1/token'
        headers_token = {
            'Authorization': 'Basic Y29sZXJvY2htYW46ZGVzaXMxMDA5fg==',
            'Content-Type': 'application/json; charset=UTF-8'
        }

        response = requests.post(url = url_token, headers=headers_token)
        response_json = response.json()

        headers_msg = {
            'Authorization': response_json['type'] + ' ' + response_json['accesstoken'],
            'Content-Type': 'application/json; charset=UTF-8'
        }
        print(headers_msg)
        return headers_msg


class BizppurioRequest(Bizppurio):
    url_msg = 'https://api.bizppurio.com/v3/message'

    def __init__(self, payload: dict):
        self.payload = payload
        self.headers_msg = self.build_headers()
        self.body_msg = self.build_body(payload)

    def build_body(self, payload: dict):
        body_msg = {
            'account': 'colerochman',
            'type': 'at',
            'from': '0221233137',
        }
        body_msg.update(payload)
        print(body_msg)
        return body_msg

    @staticmethod
    def is_success(response: Response) -> bool:
        return response.ok and json.loads(response.content).get('status') == 'OK'
    def send(self):
        response = requests.post(url=self.url_msg, headers=self.headers_msg, data=json.dumps(self.body_msg))
        response_content = json.loads(response.content)

        if self.is_success(response):
            return True, response_content
        else:
            description = get_error_desc(response_content.get('status'))
            response_content.update(description)
            return False, response_content
