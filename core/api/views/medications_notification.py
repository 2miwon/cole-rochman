import datetime

from django.http import Http404
from rest_framework.utils import json

from core.api.serializers import PatientUpdateSerializer
from core.api.util.helper import KakaoResponseAPI
from core.models import MedicationResult


def get_now():
    return datetime.datetime.now().time()


def get_recent_noti_time(noti_time_list, now_time):
    noti_time_list = [x for x in noti_time_list if x is not None]
    s = sorted(noti_time_list)
    try:
        return next(s[i - 1] for i, x in enumerate(s) if x > now_time)
    except StopIteration:
        return s[-1]


def get_recent_noti_time_num(noti_time_list, recent_noti_time):
    return [i + 1 for i, x in enumerate(noti_time_list) if x == recent_noti_time][0]


def get_recent_medication_result(patient) -> MedicationResult:
    noti_time_list = patient.medication_noti_time_list()
    now_time = get_now()
    recent_noti_time = get_recent_noti_time(noti_time_list=noti_time_list, now_time=now_time)

    if now_time > recent_noti_time:
        date = datetime.date.today()
    else:
        date = datetime.date.today() - datetime.timedelta(days=1)

    recent_medication_result = patient.medication_results.filter(medication_time=recent_noti_time, date=date)
    if recent_medication_result.exists():
        recent_medication_result = recent_medication_result.get()
    else:
        noti_time_num = get_recent_noti_time_num(noti_time_list, recent_noti_time)
        recent_medication_result = patient.create_medication_result(noti_time_num=noti_time_num, date=date)

    return recent_medication_result


class PastMedicationCheckChooseTime(KakaoResponseAPI):
    """
    deprecated. It will be deleted.
    """
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()

        if patient.medication_manage_flag and patient.daily_medication_count > 0:
            date = json.loads(self.data.get('medication_date')).get('value')

            response.add_simple_text(text='%s을 입력받았습니다. 몇 회차 복약을 변경하고 싶으신가요?' % date)
            for n in range(patient.daily_medication_count):
                response.add_quick_reply(
                    action='block',
                    label='%s회' % (n + 1),
                    message_text='%s회를 변경할게요' % (n + 1),
                    block_id='5dcdb23892690d000143800f'  # (블록) 04 지난복약체크_복약여부
                )
            return response.get_response_200()

        else:
            response.add_simple_text(text='설정된 복약 알림이 없습니다.')
            return response.get_response_200()


class PastMedicationEntrance(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()

        if (patient.medication_manage_flag is False or
                patient.daily_medication_count == 0 or
                all([True if x is None else False for x in patient.medication_noti_time_list()])):
            response.add_simple_text(text='설정된 복약 알림이 없습니다.')
        else:
            response.add_simple_text(text='잘하셨습니다!(최고)\n오늘 복약 후에 몸에 이상 반응은 없었나요?')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5dcdb23892690d000143800f',  # (블록) 04 지난복약체크_복약여부
                block_id_for_no='5dcdb40b92690d000143801a',  # (블록) 지난복약체크_탈출
                message_text_for_yes='예',
                message_text_for_no='아니요'
            )
        return response.get_response_200()


class PastMedicationSuccess(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()

        recent_medication_result = get_recent_medication_result(patient)
        recent_medication_result.set_success()  # or set_delayed_success
        recent_medication_result.save()
        return response.get_response_200_without_data()


class PastMedicationFailed(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()

        recent_medication_result = get_recent_medication_result(patient)
        recent_medication_result.set_failed()
        recent_medication_result.save()
        response.add_simple_text(text='%s님, 다음 회차에는 꼭 복약하셔야합니다. 제가 늘 응원하고 있습니다!👍' % patient.nickname)
        response.add_quick_reply(
            action='block', label='처음으로 돌아가기',
            block_id='5d732d1b92690d0001813d45'  # (블록) Generic_시작하기 처음으로
        )
        return response.get_response_200()


class PastMedicationSideEffect(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()

        recent_medication_result = get_recent_medication_result(patient)

        status_info = self.data.get('status_info')
        severity = self.data.get('severity')
        recent_medication_result.set_side_effect(status_info=status_info, severity=severity)
        recent_medication_result.save()
        response.add_simple_text(text='알려주셔서 감사합니다. 이상 반응에 대해서는 담당 의사 선생님께 꼭 말씀드리셔야합니다!☎️')
        response.add_quick_reply(
            action='block', label='처음으로 돌아가기',
            block_id='5d732d1b92690d0001813d45'  # (블록) Generic_시작하기 처음으로
        )
        return response.get_response_200()
