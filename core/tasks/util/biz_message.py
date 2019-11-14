import requests

from django.conf import settings

'''
EXAMPLE - https://www.apistore.co.kr/api/apiView.do?service_seq=558

response = Unirest.POST ("http://api.apistore.co.kr/kko/{apiVersion}/msg/{client_id}",
  headers={"x-waple-authorization": "고객 키"},
  params={
	phone:"01011112222" ,
	callback:"01033334444" ,
	reqdate:"20160517000000" ,
	msg:"내용" ,
	template_code:"01" ,
	failed_type:"LMS" ,
	failed_subject:"API스토어" ,
	failed_msg:"내용" ,
	btn_types:"배송조회,웹링크" ,
	btn_txts:"배송조회,홈페이지" ,
	btn_urls1:",http://www.apistore.co.kr" ,
	btn_urls2:",http://www.apistore.co.kr"   }
)
'''


class BizMessage():
    api_version = ''  # TODO
    url = 'http://api.apistore.co.kr/kko/{}/msg/{}'.format(api_version, settings.BIZ_MESSAGE['CLIENT_ID'])
    headers = {'x-waple-authorization': settings.BIZ_MESSAGE['API_KEY']}
    callback_number = ''  # TODO

    def __init__(self, phone_number, message, template_code, btn_types, btn_txts, btn_urls1, btn_urls2, send_at=None,
                 failed_type='SMS',
                 failed_subject='결핵박사 콜로크만', failed_msg=None):
        """
        :param phone_number:
        :param message:
        :param template_code:
        :param btn_types:
        :param btn_txts:
        :param btn_urls1:
        :param btn_urls2:
        :param send_at:
        :param failed_type:
        :param failed_subject:
        :param failed_msg:

        :type phone_number: str
        :type message: str
        :type template_code: str
        :type btn_types: str
        :type btn_txts: str
        :type btn_urls1: str
        :type btn_urls2: str
        :type send_at: str
        :type failed_type: str
        :type failed_subject: str
        :type failed_msg: str
        """

        if failed_msg is None:
            failed_msg = message
        self.data = {
            'phone': phone_number,
            'callback': self.__class__.callback_number,
            'reqdate': send_at,
            'msg': message,
            'template_code': template_code,
            'failed_type': failed_type,
            'failed_subject': failed_subject,
            'failed_msg': failed_msg,
            'btn_types': btn_types,
            'btn_txts': btn_txts,
            'btn_urls1': btn_urls1,
            'btn_urls2': btn_urls2
        }

    def send_message(self):
        cls = self.__class__
        response = requests.post(url=cls.url, headers=cls.headers, data=self.data)
        if response.ok:
            return response
        else:
            pass
