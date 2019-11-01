from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.utils import json

from core.api.serializers import PatientUpdateSerializer
from core.api.util.helper import KakaoResponseAPI


class PatientMedicationNotiTimeStart(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = PatientUpdateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()
        response_builder = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        patient.medication_manage_flag = True
        patient.medication_noti_flag = True
        patient.save()

        if patient.medication_noti_flag and not patient.need_medication_noti_time_set():
            time_list = ','.join([x.strftime('%H시 %M분') for x in patient.medication_noti_time_list()])

            message = f"이미 모든 회차 알림 설정을 마쳤습니다.\n[설정한 시간]\n{time_list}"
            response_builder.add_simple_text(text=message)

            response_builder.add_simple_text(text="복약 알림을 모두 재설정하시겠어요?")
            response_builder.set_quick_replies_yes_or_no(
                block_id_for_yes="5db30f398192ac000115f9a0")  # (블록) 02 치료 관리 재설정_복약횟수 확인
        else:
            next_undefined_number = patient.next_undefined_noti_time_number()
            message = f'{next_undefined_number:d}회차 복약 알림을 설정할까요?'
            response_builder.add_simple_text(text=message)
            response_builder.set_quick_replies_yes_or_no(
                block_id_for_yes='5da68fb1ffa7480001db0361')  # (블록) 04 치료 관리 설정_복약 알림 시간대

        return response_builder.get_response_200()


class PatientMedicationNotiSetTime(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = PatientUpdateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()
        response_builder = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)
        patient.medication_manage_flag = True
        patient.medication_noti_flag = True

        data = dict()
        medication_noti_time = self.data.get('noti_time')
        if medication_noti_time:
            time = json.loads(medication_noti_time)['value']
            next_undefined_number = patient.next_undefined_noti_time_number()

            if next_undefined_number:
                field_name = 'medication_noti_time_%d' % next_undefined_number
                data[field_name] = time

        serializer = self.get_serializer(patient, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.query_params.get('test'):
            serializer.save()

        patient.refresh_from_db()

        # check patient doesn't need medication noti time set.
        if not patient.need_medication_noti_time_set():
            time_list = ', '.join([x.strftime('%H시 %M분') for x in patient.medication_noti_time_list()])
            response_builder.add_simple_text(text="모든 회차 알림 설정을 마쳤습니다.\n[설정한 시간]\n%s" % time_list)
            response_builder.add_simple_text(text="이대로 복약 알림을 설정할까요?")
            response_builder.set_quick_replies_yes_or_no(
                block_id_for_yes="5da5ac8fb617ea00012b4363",  # (블록) 05 치료 관리 설정_알림 설정 완료
                block_id_for_no="5da549a6ffa7480001daf819",  # (블록) 01-1 치료 관리 설정_복약 관리 취소
                message_text_for_no="아니요")

            return response_builder.get_response_200()
        else:
            time = time.split(':')[0] + '시 ' + time.split(':')[1] + '분'
            response_builder.add_simple_text(text=f"{time}을 입력하셨어요.\n다음 회차를 설정하시려면 '예'를 눌러주세요.")
            response_builder.set_quick_replies_yes_or_no(
                block_id_for_yes="5da5eac292690d0001a489e4")  # (블록) 03 치료 관리 설정_복약 알림 시간

            return response_builder.get_response_200()


class PatientMedicationNotiReset(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = PatientUpdateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()

        patient.reset_medication()
        response_builder = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        response_builder.add_simple_text(text="복약 알림 설정을 취소했습니다.\n다시 설정할까요?")
        response_builder.set_quick_replies_yes_or_no(
            block_id_for_yes="5da5e59ab617ea00012b43ee")  # (블록) 02 치료 관리 설정_복약횟수

        return response_builder.get_response_200()
