import datetime

from django.http import Http404
from rest_framework.utils import json

from core.api.serializers import PatientUpdateSerializer
from core.api.util.helper import KakaoResponseAPI
from core.models import MedicationResult
from core.util.dayModule import *


# 현재 시간 이전의 가장 최근 복약 알림 시간 출력
def get_recent_noti_time(noti_time_list, now_time):
    noti_time_list = [x for x in noti_time_list if x is not None]
    s = sorted(noti_time_list)
    try:
        return next(s[i - 1] for i, x in enumerate(s) if x > now_time)
    except StopIteration:
        if s:
            return s[-1]


# recent_noti_time이 오늘 복약의 몇 번째 복약 알림인지를 출력
def get_recent_noti_time_num(noti_time_list, recent_noti_time):
    return [i + 1 for i, x in enumerate(noti_time_list) if x == recent_noti_time][0]


# 가장 최근 복약 알림을 Model로 가져옴
def get_recent_medication_result(patient) -> MedicationResult:
    noti_time_list = patient.medication_noti_time_list()
    now_time = get_now_time()
    recent_noti_time = get_recent_noti_time(
        noti_time_list=noti_time_list, now_time=now_time
    )
    if now_time > recent_noti_time:
        date = datetime.date.today()
    else:
        date = datetime.date.today() - datetime.timedelta(days=1)

    recent_medication_result = patient.medication_results.filter(
        medication_time=recent_noti_time, date=date
    )
    if recent_medication_result.exists():
        recent_medication_result = recent_medication_result.get()
    else:
        noti_time_num = get_recent_noti_time_num(noti_time_list, recent_noti_time)
        recent_medication_result = patient.create_medication_result(
            noti_time_num=noti_time_num, date=date
        )

    return recent_medication_result


# 복약 체크 시작
class PastMedicationEntrance(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format="json", *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()

        if (
            patient.medication_manage_flag is False
            or patient.daily_medication_count == 0
            or all(
                [
                    True if x is None else False
                    for x in patient.medication_noti_time_list()
                ]
            )
        ):
            response.add_simple_text(text="설정된 복약 알림이 없습니다.")
        else:
            response.add_simple_text(text="잘하셨습니다!👍\n지난번 복약 후에 몸에 이상 반응이 있었나요")
            response.set_quick_replies_yes_or_no(
                block_id_for_yes="63057f66afbe4b38b58bceac",  # (블록) 부작용 카테고리
                block_id_for_no="5dd43c5a92690d000194d94c",  # (블록) 지난복약체크_탈출
                message_text_for_yes="예",
                message_text_for_no="아니요",
            )
        return response.get_response_200()


# 복약성공 체크
class PastMedicationSuccess(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format="json", *args, **kwargs):
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


# 복약실패 확인 (현재 사용 안 함)
class PastMedicationFailed(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format="json", *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()

        recent_medication_result = get_recent_medication_result(patient)
        recent_medication_result.set_failed()
        recent_medication_result.save()
        response.add_simple_text(
            text="%s님, 다음 회차에는 꼭 복약하셔야합니다. 제가 늘 응원하고 있습니다!" % patient.nickname
        )
        response.add_quick_reply(
            action="block",
            label="처음으로 돌아가기",
            block_id="5d732d1b92690d0001813d45",  # (블록) Generic_시작하기 처음으로
        )
        return response.get_response_200()


class PastMedicationSideEffect(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format="json", *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        severity_name = self.data.get("severity_name")

        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()

        recent_medication_result = get_recent_medication_result(patient)

        if self.data.get("symptom_severity1"):
            severity1 = self.data.get("symptom_severity1")
        else:
            severity1 = "선택 없음"
        if self.data.get("symptom_severity2"):
            severity2 = self.data.get("symptom_severity2")
        else:
            severity2 = "선택 없음"
        if self.data.get("symptom_severity3"):
            severity3 = self.data.get("symptom_severity3")
        else:
            severity3 = "선택 없음"
        if recent_medication_result.symptom_name:
            recent_medication_result.add_side_effect(
                name=severity_name,
                severity1=severity1,
                severity2=severity2,
                severity3=severity3,
            )
        else:
            recent_medication_result.set_side_effect(
                name=severity_name,
                severity1=severity1,
                severity2=severity2,
                severity3=severity3,
            )
        recent_medication_result.save()

        if severity2 == "매우 심하다" or severity3 == "매우 많이 주었다":
            response.add_simple_text(text="혹시 해당 부작용과 관련하여 상담원 연결을 원하십니까?")
            response.set_quick_replies_yes_or_no(
                block_id_for_yes="6309bb67afbe4b38b58c1609",  # (블록) 상담원 연결
                block_id_for_no="62fe8a908a1240569898eb17",  # (블록) 부작용 기록 완료
                message_text_for_yes="예",
                message_text_for_no="아니요",
            )
        else:
            response.add_simple_text(text="부작용 기록을 완료했습니다.\n다른 부작용을 추가로 기록하시겠습니까?")
            response.set_quick_replies_yes_or_no(
                block_id_for_yes="63057f66afbe4b38b58bceac",  # (블록) 부작용 카테고리
                block_id_for_no="5d732d1b92690d0001813d45",  # (블록) Generic_시작하기 처음으로
                message_text_for_yes="예(부작용 카테고리로)",
                message_text_for_no="아니요(처음으로)",
            )
        return response.get_response_200()
