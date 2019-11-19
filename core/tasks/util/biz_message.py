import datetime

import requests

from enum import Enum
from django.conf import settings

from core.models import Patient

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


class TYPE(Enum):
    MORNING_MEDI_MANAGEMENT_TRUE = 'morning_medi_managament_true'
    MORNING_MEDI_MANAGEMENT_FALSE = 'morning_medi_management_false'
    MORNING_MEDI_MANAGEMENT_TRUE_AND_VISIT_TODAY = 'morning_medi_management_true_and_visit_today'
    MORNING_MEDI_MANAGEMENT_FALSE_AND_VISIT_TODAY = 'morning_medi_management_false_and_visit_today'

    MEDICATION_NOTI = 'medication_noti'
    VISIT_NOTI = 'visit_noti'

    def __init__(self, patient: Patient):
        self.patient = patient

    def __call__(self, *args, **kwargs):
        return self.get_morning_notification()

    def get_morning_notification(self):
        if self.patient.medication_manage_flag:
            if self.patient.next_visiting_date_time == datetime.datetime.today():
                return self.MORNING_MEDI_MANAGEMENT_TRUE_AND_VISIT_TODAY
            else:
                return self.MORNING_MEDI_MANAGEMENT_TRUE
        else:
            if self.patient.next_visiting_date_time == datetime.datetime.today():
                return self.MORNING_MEDI_MANAGEMENT_FALSE_AND_VISIT_TODAY
            else:
                return self.MORNING_MEDI_MANAGEMENT_FALSE


class Buttons:
    def __init__(self, type: str):
        if type not in list(TYPE.__members__.values()):
            raise ValueError('type is not in TYPE ENUM: %s' % list(TYPE.__members__.values()).__str__())

        self.type = type

    @property
    def needs_button(self):
        return self.type not in [TYPE.MORNING_MEDI_MANAGEMENT_TRUE,
                                 TYPE.MORNING_MEDI_MANAGEMENT_FALSE,
                                 TYPE.MORNING_MEDI_MANAGEMENT_TRUE_AND_VISIT_TODAY,
                                 TYPE.MORNING_MEDI_MANAGEMENT_FALSE_AND_VISIT_TODAY]

    def to_dict(self):
        data = {'btn_types': '봇키워드'}
        txts = ''
        if not self.needs_button:
            return {}

        if self.type == TYPE.MEDICATION_NOTI:
            txts = ['복약했어요', '복약 안할래요']

        if type(txts) == str:
            data['btn_txts'] = txts
        else:
            data['btn_txts'] = ','.join(txts)

        return data


class Message:
    msg = ''
    template_code = ''

    def __init__(self, type: TYPE, patient: Patient, noti_time: int, template_code: str):
        self.type = type
        self.patient = patient
        self.noti_time = noti_time
        self.template_code = template_code
        self.build_message()

    def __call__(self, *args, **kwargs):
        return self.msg

    def build_message(self):
        days_after_treatment = datetime.datetime.today().day - self.patient.treatment_started_date.day
        msg = ''
        if self.type == TYPE.MORNING_MEDI_MANAGEMENT_TRUE:
            msg = f'{self.patient.nickname}님, 오늘은 좀 어떠신지요!\n' \
                f'오늘은 결핵 치료를 시작한지 {days_after_treatment}일째입니다.\n\n' \
                f'복약은 {self.patient.medication_noti_time_list_to_str()}에 하셔야 합니다.' \
                f'잊지 않으셨지요? 그럼 저와 함께 오늘도 화이팅입니다!👍'

        elif self.type == TYPE.MORNING_MEDI_MANAGEMENT_FALSE:
            msg = f'{self.patient.nickname}님, 안녕하십니까! 좋은 아침입니다.\n' \
                f'오늘은 결핵 치료를 시작한지 {days_after_treatment}일째 입니다.\n저와 함께 힘찬 하루 시작해봅시다!☀️'

        elif self.type == TYPE.MORNING_MEDI_MANAGEMENT_TRUE_AND_VISIT_TODAY:
            visitng_time = self.patient.next_visiting_date_time.strftime('%H시 %M분')

            msg = f'{self.patient.nickname}님, 안녕하십니까! 아침은 드셨나요?🍚' \
                f'오늘은 결핵 치료를 시작한지 {days_after_treatment}일째 입니다.' \
                f'복약은 {self.patient.medication_noti_time_list_to_str()}에 하셔야 합니다.💊' \
                f'오늘은 {visitng_time}에 병원에 가셔야 하는군요.' \
                f'오늘 하루도 제가 응원하겠습니다!👍'

        elif self.type == TYPE.MORNING_MEDI_MANAGEMENT_FALSE_AND_VISIT_TODAY:
            visitng_time = self.patient.next_visiting_date_time.strftime('%H시 %M분')
            msg = f'{self.patient.nickname}님, 오늘은 좀 어떠신지요!\n' \
                f'오늘은 결핵 치료를 시작한지 {days_after_treatment}일째입니다.\n\n' \
                f'오늘 {visitng_time}에 병원에 가셔야 하는 것, 잊지않으셨죠?🎶'

        elif self.type == TYPE.MEDICATION_NOTI:
            msg = f"{self.noti_time}회차 복약을 하실 시간입니다.💊\n" \
                f"복약 후에 아래 '복약했어요' 버튼을 눌러주십시오.\n" \
                f"제가 더욱 꼼꼼한 관리를 도와드리겠습니다!"

        self.msg = msg


class BizMessage:
    api_version = ''  # TODO
    url = 'http://api.apistore.co.kr/kko/{}/msg/{}'.format(api_version, settings.BIZ_MESSAGE['CLIENT_ID'])
    headers = {'x-waple-authorization': settings.BIZ_MESSAGE['API_KEY']}
    callback_number = settings.BIZ_MESSAGE['CALLBACK_NUMBER']

    def __init__(self, phone_number, message, template_code, btn_types, btn_txts, btn_urls1, btn_urls2,
                 send_at=None,
                 failed_type='SMS',
                 failed_subject='결핵박사 콜로크만', failed_msg=None):
        """
        :param phone_number: 수신할 핸드폰 번호 ex. 01011112222
        :param message: 전송할 메세지
        :param template_code: 카카오 알림톡 템플릿 코드 ex. 01
        :param btn_types: 버튼이 여러개일때 버튼타입배열 ,(콤마)로 구분합니다  ex. 배송조회,웹링크
        :param btn_txts: 버튼이 여러개일때 버튼명배열 ,(콤마)로 구분합니다  ex. 배송조회,홈페이지
        :param btn_urls1: 버튼이 여러개일때 URL1배열 ,(콤마)로 구분합니다.  ex. ,http://www.apistore.co.kr
        :param btn_urls2: 버튼이 여러개일때 URL2배열 ,(콤마)로 구분합니다.  ex. ,http://www.apistore.co.kr
        :param send_at: 발송시간(없을 경우 즉시 발송) ex. 20160517000000
        :param failed_type: 카카오 알림톡 전송 실패 시 전송할 메시지 타입 ex. LMS
        :param failed_subject: 카카오 알림톡 전송 실패 시 전송할 제목
        :param failed_msg: 카카오 알림톡 전송 실패 시 전송할 내용

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
            'callback': self.__class__.callback_number,  # 발신자 전화번호
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

    def to_dict(self):
        return self.data

    def send_message(self):
        cls = self.__class__
        response = requests.post(url=cls.url, headers=cls.headers, data=self.data)
        if response.ok:
            return response
        else:
            pass
