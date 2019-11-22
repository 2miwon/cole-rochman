import datetime
from enum import Enum

import requests
from django.conf import settings

from core.models import Patient
from core.tasks.util.ncloud import NcloudRequest


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
        return self.get_morning_noti_type()

    def get_morning_noti_type(self):
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
    button_type = 'BK'

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

    @classmethod
    def build_buttons_medicated_or_not(cls) -> list:
        data = [
            {
                'type': cls.button_type,
                'name': '복약했어요',
            },
            {
                'type': cls.button_type,
                'name': '복약 안할래요',
            }
        ]
        return data

    def to_dict(self) -> list:
        buttons = []
        if not self.needs_button:
            return []

        if self.type == TYPE.MEDICATION_NOTI:
            buttons = self.build_buttons_medicated_or_not()

        return buttons


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


class BizMessage(NcloudRequest):
    """
    https://apidocs.ncloud.com/ko/ai-application-service/sens/alimtalk_v2/
    """
    method = 'POST'
    uri = 'https://sens.apigw.ntruss.com/alimtalk/v2/services/{}/messages'.format(settings.BIZ_MESSAGE['SERVICE_ID'])
    callback_number = settings.BIZ_MESSAGE['CALLBACK_NUMBER']

    plus_friend_id = settings.BIZ_MESSAGE['PLUS_FRIEND_ID']

    def __init__(self, phone_number: str, content: str, template_code: str, buttons: list = None,
                 reserve_time: str = None, schedule_code: str = None):
        """
        :param phone_number:
        :param content:
        :param template_code:
        :param buttons:
        :param reserve_time: yyyy-MM-dd HH:mm
        :param schedule_code:
        """
        self.headers = self.build_headers()

        self.payload = {
            'plusFriendId': self.plus_friend_id,
            'templateCode': template_code,
            'messages': [
                {
                    'to': phone_number,
                    'content': content,

                }
            ],
        }

        if buttons:
            self.payload['messages'].update(
                {
                    'buttons': buttons
                }
            )

        if reserve_time and schedule_code:
            self.payload.update(
                {
                    'reserveTime': reserve_time,
                    'reserveTimeZone': 'Asia/Seoul',
                    'scheduleCode': schedule_code
                }
            )

    def to_dict(self):
        return self.payload

    def send_message(self):
        cls = self.__class__
        response = requests.post(url=cls.uri, headers=self.headers, data=self.payload)
        if response.ok:
            return response
        else:
            pass
