import datetime
import json

from rest_framework import status
from rest_framework.response import Response

from core.api.serializers import PatientCreateSerializer
from core.api.util.helper import KakaoResponseAPI


class PatientVisitDateSet(KakaoResponseAPI):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        patient = self.get_object_by_kakao_user_id()
        response_builder = self.build_response(response_type=self.RESPONSE_SKILL)

        next_visiting_date_time = request.data['action']['params']['next_visiting_date_time']
        data = dict()
        data['visit_manage_flag'] = True

        if next_visiting_date_time:
            # "value": "{\"value\":\"2018-03-20T10:15:00\",\"userTimeZone\":\"UTC+9\"}",
            value = json.loads(next_visiting_date_time)['value']
            value = datetime.datetime.strptime(value, self.DATETIME_FORMAT_STRING)
            data['next_visiting_date_time'] = value.astimezone()

        serializer = self.get_serializer(patient, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.query_params.get('test'):
            serializer.save()

        patient.refresh_from_db()

        response_builder.add_simple_text(text="%s이 내원일이군요." % patient.next_visiting_date_time_str())
        response_builder.add_simple_text(text="내원 알람을 설정할까요?")
        response_builder.set_quick_replies_yes_or_no(block_id_for_yes="5d9df34e92690d0001a458ed",
                                                     message_text_for_no="아니요")  # (블록) 03 치료 관리 설정_내원 알람 설정

        return response_builder.get_response_200()


class PatientVisitNotiTimeBefore(KakaoResponseAPI):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        patient = self.get_object_by_kakao_user_id()
        response_builder = self.build_response(response_type=self.RESPONSE_SKILL)

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

        response_builder.add_simple_text(text="내원 시간 %s 전에 알람을 드리겠습니다." % time_before_verbose.strip())
        response_builder.add_simple_text(text="이대로 알람을 설정할까요?")
        response_builder.set_quick_replies_yes_or_no(block_id_for_yes="5d9df7978192ac0001156891",
                                                     # (블록) 05 치료 관리 설정_내원 관리 완료
                                                     block_id_for_no="5d9df9368192ac00011568a9",
                                                     # (블록) 치료 관리 설정_내원 알람 종료
                                                     message_text_for_no="아니요, 지금은 안 할래요.")

        return response_builder.get_response_200()
