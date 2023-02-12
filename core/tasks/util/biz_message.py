import datetime
from enum import Enum
import random

from core.models import Patient


class TYPE(Enum):
    MORNING_MEDI_MANAGEMENT_TRUE = 'bizp_2022091116122766345661257'
    MORNING_MEDI_MANAGEMENT_FALSE = ''
    MORNING_MEDI_MANAGEMENT_TRUE_AND_VISIT_TODAY = 'bizp_2022100415272341820951946'
    MORNING_MEDI_MANAGEMENT_FALSE_AND_VISIT_TODAY = 'bizp_2022100415335018895899977'

    MEDICATION_NOTI = 'bizp_2022100415563518895908981'
    VISIT_NOTI = 'bizp_2022100416040318895140984'

    @classmethod
    def get_morning_noti_type(cls, patient: Patient):
        medi_management = patient.medication_manage_flag and patient.medication_noti_time_list_to_str()

        if patient.next_visiting_date_time:
            visit_today = patient.next_visiting_date_time.date() == datetime.datetime.today().astimezone().date()
        else:
            visit_today = None

        if medi_management and visit_today:
            return cls.MORNING_MEDI_MANAGEMENT_TRUE_AND_VISIT_TODAY

        elif medi_management and not visit_today:
            return cls.MORNING_MEDI_MANAGEMENT_TRUE

        elif not medi_management and visit_today:
            return cls.MORNING_MEDI_MANAGEMENT_FALSE_AND_VISIT_TODAY

        elif not medi_management and not visit_today:
            return cls.MORNING_MEDI_MANAGEMENT_FALSE


class Message:
    msg = ''
    template_code = ''

    def __init__(self, type: TYPE, patient: Patient, date: datetime.date, noti_time_num: int = None):
        self.type = type
        self.patient = patient
        self.date = date
        self.noti_time_num = noti_time_num
        self.template_code = type.value

        self.build_message()

    def __call__(self, *args, **kwargs):
        return self.msg

    def build_message(self) -> str:
        try:
            days_after_treatment = (datetime.datetime.today().date() - self.patient.treatment_started_date).days
        except TypeError:
            days_after_treatment = 0

        msg = ''
#        if self.type == TYPE.MORNING_MEDI_MANAGEMENT_TRUE:
#            msg = f'{self.patient.nickname}님, 오늘은 좀 어떠신지요!\n' \
#                f'오늘은 결핵 치료를 시작한지 {days_after_treatment}일째입니다.\n\n' \
#                f'복약은 {self.patient.medication_noti_time_list_to_str()}에 하셔야 합니다.\n' \
#                f'잊지 않으셨지요? 그럼 저와 함께 오늘도 화이팅입니다!'
#            msg = f'{self.patient.nickname}님, 오늘은 좀 어떠신지요!\n' \
#                f'오늘은 결핵 치료를 시작한지 {days_after_treatment}일째입니다.☀️\n\n' \
#                f'복약은 {self.patient.medication_noti_time_list_to_str()}에 하셔야 합니다. ' \
#                f'잊지 않으셨지요? 그럼 저와 함께 오늘도 화이팅입니다!👍'

#        elif self.type == TYPE.MORNING_MEDI_MANAGEMENT_FALSE:
#            msg = f'{self.patient.nickname}님, 안녕하십니까! 좋은 아침입니다.\n' \
#                f'오늘은 결핵 치료를 시작한지 {days_after_treatment}일째 입니다.\n저와 함께 힘찬 하루 시작해봅시다!☀️'

#        elif self.type == TYPE.MORNING_MEDI_MANAGEMENT_TRUE_AND_VISIT_TODAY:
#            visiting_time = self.patient.next_visiting_date_time.strftime('%H시 %M분')
#            msg = f'{self.patient.nickname}님, 안녕하십니까! 아침은 드셨나요?(밥)\n' \
#                f'오늘은 결핵 치료를 시작한지 {days_after_treatment}일째입니다.\n\n' \
#                f'복약은 {self.patient.medication_noti_time_list_to_str()}에 하셔야 합니다.(알약)\n' \
#                f'오늘은 {visiting_time}에 병원에 가셔야 하는군요.\n' \
#                f'오늘 하루도 제가 응원하겠습니다!(최고)'
#                f'{self.patient.nickname}님, 안녕하십니까! 아침은 드셨나요?🍚' \
#                f'오늘은 결핵 치료를 시작한지 {days_after_treatment}일째 입니다.\n\n' \
#                f'복약은 {self.patient.medication_noti_time_list_to_str()}에 하셔야 합니다.💊\n\n' \
#                f'오늘은 {visitng_time}에 병원에 가셔야 하는군요.\n\n' \
#                f'오늘 하루도 제가 응원하겠습니다!👍'

#        elif self.type == TYPE.MORNING_MEDI_MANAGEMENT_FALSE_AND_VISIT_TODAY:
#            visiting_time = self.patient.next_visiting_date_time.strftime('%H시 %M분')
#            msg = f'{self.patient.nickname}님, 오늘은 좀 어떠신지요!\n' \
#                f'오늘은 결핵 치료를 시작한지 {days_after_treatment}일째입니다.\n\n' \
#                f'오늘 {visiting_time}에 병원에 가셔야 하는 것, 잊지 않으셨죠?(>음표)\n' \
#                f'저와 함께 오늘도 화이팅입니다!(최고)'
#                msg = f'{self.patient.nickname}님, 오늘은 좀 어떠신지요!\n' \
#                f'오늘은 결핵 치료를 시작한지 {days_after_treatment}일째입니다.\n\n' \
#                f'오늘 {visitng_time}에 병원에 가셔야 하는 것, 잊지않으셨죠?🎶'

        if self.type == TYPE.MEDICATION_NOTI:
            msg = f'{self.noti_time_num}회차 복약을 하실 시간입니다.(알약)\n' \
                f'복약 후에 복약을 기록해주십시오.\n' \
                f'제가 더욱 꼼꼼한 관리를 도와드리겠습니다!'
#            msg = f'{self.noti_time_num}회차 복약을 하실 시간입니다.💊\n' \
#                f'복약 후에 아래 \'복약했어요\' 버튼을 눌러주십시오.\n' \
#                f'제가 더욱 꼼꼼한 관리를 도와드리겠습니다!'

        elif self.type == TYPE.VISIT_NOTI:
            expecting_time = datetime.timedelta(seconds=self.patient.visit_notification_before)
            days = expecting_time.days
            time = (datetime.datetime.min + expecting_time).time()

            if days == 1:
                expecting_time = '내일'
            elif days == 2:
                expecting_time = '내일 모레'
            elif days > 2:
                expecting_time = f'{days}일 후'
            elif time.minute:
                expecting_time = f'{time.hour}시간 {time.minute}분 후'
            else:
                expecting_time = f'{time.hour}시간 후'

            msg = f'{expecting_time} 병원에 가셔야 합니다.\n' \
                f'조심히 다녀오십시오!(최고)'
#            msg = f'{expecting_time} 병원에 가셔야 합니다.\n조심히 다녀오십시오!👍'

        self.msg = msg
        return msg


class BizMessageBuilder:
    def __init__(self, message_type: TYPE or str, patient: Patient, date: datetime.date, noti_time_num: int = None):
        if type(message_type) is str:
            message_type = TYPE(message_type)

        self.message_type = message_type
        template_code = message_type.value

        self.template_code = template_code
        self.message = Message(type=message_type, patient=patient, date=date, noti_time_num=noti_time_num)
        
        refkey = str(random.randrange(100000000000, 999999999999))
        self.payload = {
            'refkey': refkey,
            'to': patient.phone_number,
            'content': {
                'at': {
                    'senderkey': '707d67503ebf7d3a24a7df6eee1e467cb90269ee',
                    'templatecode': self.template_code,
                    'message': self.message.msg,
                }
            }
        }

    def to_dict(self):
        if self.message.msg == '':
            return {}
        return self.payload
