import datetime
import json

from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from core.api.serializers import PatientUpdateSerializer
from core.api.util.helper import KakaoResponseAPI


class PatientVisitStart(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()
        response = self.build_response(response_type=self.RESPONSE_SKILL)
        if patient.visit_manage_flag and patient.next_visiting_date_time is not None:
            response.add_simple_text(
                '이미 내원일을 설정하신 적이 있어요.\n현재 설정된 내원 예정일: %s\n\n내원 일정을 수정하시겠습니까?' % patient.next_visiting_date_time_str())
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5db314e38192ac000115f9af',  # (블록) 02 치료 관리 재설정_내원 예정일 설정
                block_id_for_no='5d9df7dfb617ea00012b17f3'  # (블록) 치료 관리 설정_내원 관리 종료
            )
            return response.get_response_200()

        if patient.discharged_flag:
            response.add_simple_text(text='내원 관리를 시작하시겠습니까?')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5d9df31692690d0001a458e6',  # (블록) 02 치료 관리 설정_내원 예정일 확인
                block_id_for_no='5dd102f0b617ea0001b5a294'  # (블록) 00 대화 종료 여부_내원관리
            )
            return response.get_response_200()
        else:
            response.add_simple_text(text='아직 퇴원을 하지 않으셔서 내원 관리를 하실 필요가 없어요.')
            response.add_simple_text(text='치료 관리 모드로 이동할까요?')
            response.add_simple_text(text='(아직 이동할 블록이 설정되지 않았습니다.)')
            # TODO 치료관리 모드 의 블록이 확실해지면 block_id 넣기
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5dbc2eac92690d0001e876d6'
            )
            return response.get_response_200()


class PatientVisitDateSet(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)

        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()

        response = self.build_response(response_type=self.RESPONSE_SKILL)
        next_visiting_date_time = request.data['action']['params'].get('next_visiting_date_time')
        data = dict()
        data['visit_manage_flag'] = True

        if next_visiting_date_time:
            # "value": "{\"value\":\"2018-03-20T10:15:00\",\"userTimeZone\":\"UTC+9\"}",
            value = json.loads(next_visiting_date_time)['value']
            value = datetime.datetime.strptime(value, self.DATETIME_STRPTIME_FORMAT)
            data['next_visiting_date_time'] = value.astimezone()

        serializer = self.get_serializer(patient, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.query_params.get('test'):
            serializer.save()

        patient.refresh_from_db()

        response.add_simple_text(text="%s이 내원일이군요." % patient.next_visiting_date_time_str())
        response.add_simple_text(text="내원 알림을 설정할까요?☀️")
        response.set_quick_replies_yes_or_no(block_id_for_yes="5d9df34e92690d0001a458ed",  # (블록) 03 치료 관리 설정_내원 알람 설정
                                             block_id_for_no="5dd1036492690d000194b9fb",  # (블록) 00 대화 종료 여부_내원알림
                                             message_text_for_no="아니요")

        return response.get_response_200()


class PatientVisitNotiTimeBefore(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()

        response = self.build_response(response_type=self.RESPONSE_SKILL)

        seconds = self.data['visit_notification_before']  # 초 단위의 integer
        seconds = int(seconds)
        data = dict()
        data['visit_notification_before'] = seconds
        data['visit_notification_flag'] = True

        serializer = self.get_serializer(patient, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.query_params.get('test'):
            serializer.save()

        timedelta = datetime.timedelta(seconds=seconds)
        time_before_verbose = ''

        timedelta_hours = seconds // (60 * 60)
        timedelta_minutes = (seconds // 60) - (timedelta_hours * 60)

        if timedelta.days:
            time_before_verbose += '%d일 ' % timedelta.days
        if not timedelta_hours == 0:
            time_before_verbose += '%d시간 ' % timedelta_hours
        if not timedelta_minutes == 0:
            time_before_verbose += '%d분 ' % timedelta_minutes

        response.add_simple_text(text="내원 시간 %s 전에 알림을 드리겠습니다." % time_before_verbose.strip())
        response.add_simple_text(text="이대로 알림을 설정할까요?")
        response.set_quick_replies_yes_or_no(block_id_for_yes="5d9df7978192ac0001156891",
                                             # (블록) 05 치료 관리 설정_내원 관리 완료
                                             block_id_for_no="5d9df9368192ac00011568a9",
                                             # (블록) 치료 관리 설정_내원 알림 종료
                                             message_text_for_no="아니요, 지금은 안 할래요.")

        return response.get_response_200()


class PatientVisitRestart(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=self.RESPONSE_SKILL)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()

        if patient.visit_manage_flag and patient.next_visiting_date_time is not None:
            response.add_simple_text('내원 일정을 수정하시겠습니까?\n현재 설정된 내원 예정일: %s' % patient.next_visiting_date_time_str())
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5db314e38192ac000115f9af',  # (블록) 02 치료 관리 재설정_내원 예정일 설정
                block_id_for_no='5da549bcffa7480001daf821'  # (블록) 치료 관리 설정_시작하기 처음으로
            )
        else:
            response.add_simple_text('설정된 내원일이 없습니다.\n내원 관리를 새로 설정하러 가볼까요?')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5d9df0a9ffa7480001dacfd7',  # (블록) 01 치료 관리 설정_내원 관리 시작
                block_id_for_no='5da549bcffa7480001daf821'  # (블록) 치료 관리 설정_시작하기 처음으로
            )

        return response.get_response_200()
