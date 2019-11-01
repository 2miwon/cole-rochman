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
        patient = self.get_object_by_kakao_user_id()
        response_builder = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        patient.medication_manage_flag = True
        patient.medication_noti_flag = True
        patient.save()

        if patient.medication_noti_flag and not patient.need_medication_noti_time_set():
            time_list = ','.join([x.strftime('%H시 %M분') for x in patient.medication_noti_time_list()])

            message = f"이미 모든 회차 알림 설정을 마쳤습니다.\n[설정한 시간]\n{time_list}"
            response_builder.add_simple_text(text=message)

            # TODO 다음 액션 없음
            # TODO-2 시간 재설정할건지 물어보면 좋을 듯
        else:
            next_undefined_number = patient.next_undefined_noti_time_number()
            message = f'{next_undefined_number:d}회차 복약 알람을 설정할까요?'
            response_builder.add_simple_text(text=message)
            response_builder.set_quick_replies_yes_or_no(
                block_id_for_yes='5da68fb1ffa7480001db0361')  # (블록) 04 치료 관리 설정_복약 알림 시간대

        return response_builder.get_response_400()


class PatientMedicationNotiSetTime(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = PatientUpdateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        patient = self.get_object_by_kakao_user_id()
        response_builder = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        if patient.medication_noti_flag and not patient.need_medication_noti_time_set():
            times_str = ''

            for index, time in enumerate(patient.medication_noti_time_list()):
                times_str += '%d회차 알람 시간은 %s\n' % (index + 1, time.strftime('%H시 %M분'))

            times_str += '입니다.'
            response_builder.add_simple_text(text="모든 회차 알림 설정을 마쳤습니다.\n%s" % times_str)
            response_builder.add_simple_text(text="이대로 복약 알람을 설정할까요?")
            response_builder.set_quick_replies_yes_or_no(message_text_for_no="아니요",
                                                         block_id_for_yes="5da5ac8fb617ea00012b4363")  # (블록) 06 치료 관리 설정_알람 설정 완료

            return Response(response_builder.get_response(), status=status.HTTP_200_OK)

        data = dict()
        medication_noti_time = request.data['action']['params']['noti_time']
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

        if patient.medication_noti_flag and not patient.need_medication_noti_time_set():
            time_list = ', '.join([x.strftime('%H시 %M분') for x in patient.medication_noti_time_list()])
            response_builder.add_simple_text(text="모든 회차 알림 설정을 마쳤습니다.\n[설정한 시간]\n%s" % time_list)
            response_builder.add_simple_text(text="내원 관리를 시작할까요?")
            # TODO 퇴원환자의 경우 내원관리로 가면 안됨
            response_builder.set_quick_replies_yes_or_no(
                block_id_for_yes="5d9df31692690d0001a458e6")  # (블록) 02 치료 관리 설정_내원 예정일 확인

            return Response(response_builder.get_response(), status=status.HTTP_200_OK)

        response_builder.add_simple_text(text="다음 회차를 설정하시려면 '예'를 눌러주세요.")
        response_builder.set_quick_replies_yes_or_no(
            block_id_for_yes="5da5eac292690d0001a489e4")  # (블록) 03 치료 관리 설정_복약 알림 시간

        return Response(response_builder.get_response(), status=status.HTTP_200_OK)


class PatientMedicationNotiReset(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = PatientUpdateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        patient = self.get_object_by_kakao_user_id()
        patient.reset_medication_noti()
        response_builder = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        response_builder.add_simple_text(text="복약 알람 설정을 취소했습니다.\n다시 설정할까요?")
        response_builder.set_quick_replies_yes_or_no(
            block_id_for_yes="5da5e59ab617ea00012b43ee")  # (블록) 02 치료 관리 설정_복약횟수

        return Response(response_builder.get_response(), status=status.HTTP_200_OK)
