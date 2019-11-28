from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.utils import json

from core.api.serializers import PatientUpdateSerializer
from core.api.util.helper import KakaoResponseAPI


class PatientMedicationEntrance(KakaoResponseAPI):
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

        if patient.medication_manage_flag:
            response.add_simple_text('안녕하세요 콜로크만입니다.\n지난 번, 복약 관리를 설정한 적이 있습니다.\n다시 설정할까요?')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5db30f398192ac000115f9a0',  # (블록) 02 치료 관리 재설정_복약횟수 확인
                block_id_for_no='5da549bcffa7480001daf821'  # (블록) 치료 관리 설정_시작하기 처음으로
            )
            response.add_context(name='복약관리재시작', params={'daily_medication_count': patient.daily_medication_count})
        else:
            response.add_simple_text(text='안녕하세요 콜로크만입니다.\n저와 함께 복약 관리를 시작하시겠습니까?')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5da5e59ab617ea00012b43ee',  # (블록) 02 치료 관리 설정_복약횟수
                block_id_for_no='5dc72a7492690d0001caebba',  # (블록) 00 대화 종료 여부_복약관리
                message_text_for_no='아니요'
            )
        return response.get_response_200()


class PatientMedicationNotiTimeQuestion(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        patient.medication_manage_flag = True
        patient.medication_noti_flag = True
        patient.save()

        if not patient.need_medication_noti_time_set() and len(patient.medication_noti_time_list()) != 0:
            time_list = ','.join([x.strftime('%H시 %M분') for x in patient.medication_noti_time_list()])

            message = f"이미 모든 회차 알림 설정을 마쳤습니다.\n[설정한 시간]\n{time_list}"
            response.add_simple_text(text=message)

            response.add_simple_text(text="복약 알림을 모두 재설정하시겠어요?")
            response.set_quick_replies_yes_or_no(
                block_id_for_yes="5db30f398192ac000115f9a0")  # (블록) 02 치료 관리 재설정_복약횟수 확인
        else:
            next_undefined_number = patient.next_undefined_medication_noti_time_number()
        message = f'{next_undefined_number:d}회차 복약 알림을 설정할까요?'
        response.add_simple_text(text=message)
        response.set_quick_replies_yes_or_no(
            block_id_for_yes='5da68fb1ffa7480001db0361')  # (블록) 04 치료 관리 설정_복약 알림 시간대

        return response.get_response_200()


class PatientMedicationNotiTimeQuestionRestart(KakaoResponseAPI):
    """
    Different response with PatientMedicationNotiTimeQuestion
    """
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        patient.medication_manage_flag = True
        patient.medication_noti_flag = True
        patient.save()

        if not patient.need_medication_noti_time_set() and len(patient.medication_noti_time_list()) != 0:
            time_list = ','.join([x.strftime('%H시 %M분') for x in patient.medication_noti_time_list()])

            message = f"이미 모든 회차 알림 설정을 마쳤습니다.\n[설정한 시간]\n{time_list}"
            response.add_simple_text(text=message)

            response.add_simple_text(text="복약 알림을 모두 재설정하시겠어요?")
            response.set_quick_replies_yes_or_no(
                block_id_for_yes="5db30f398192ac000115f9a0")  # (블록) 02 치료 관리 재설정_복약횟수 확인
        else:
            next_undefined_number = patient.next_undefined_medication_noti_time_number()
            message = f'{next_undefined_number:d}회차 복약 알림을 설정할까요?'
            response.add_simple_text(text=message)
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5db3129e8192ac000115f9a8')  # (블록) 05 치료 관리 재설정_복약 알림 시간대

        return response.get_response_200()


class PatientMedicationNotiSetTime(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)
        patient.medication_manage_flag = True
        patient.medication_noti_flag = True

        data = dict()
        medication_noti_time = self.data.get('noti_time')
        if medication_noti_time:
            time = json.loads(medication_noti_time)['value']
            next_undefined_number = patient.next_undefined_medication_noti_time_number()

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
            response.add_simple_text(text="모든 회차 알림 설정을 마쳤습니다.\n[설정한 시간]\n%s" % time_list)
            response.add_simple_text(text="이대로 복약 알림을 설정할까요?")
            response.set_quick_replies_yes_or_no(
                block_id_for_yes="5da5ac8fb617ea00012b4363",  # (블록) 05 치료 관리 설정_알림 설정 완료
                block_id_for_no="5da549a6ffa7480001daf819",  # (블록) 01-1 치료 관리 설정_복약 관리 취소
                message_text_for_no="아니요")

            return response.get_response_200()
        else:
            time = time.split(':')[0] + '시 ' + time.split(':')[1] + '분'
            response.add_simple_text(text=f"{time}을 입력하셨어요.\n다음 회차를 설정하시려면 '예'를 눌러주세요.")
            response.set_quick_replies_yes_or_no(
                block_id_for_yes="5da5eac292690d0001a489e4")  # (블록) 03 치료 관리 설정_복약 알림 시간

            return response.get_response_200()


class PatientMedicationNotiSetTimeInRestart(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)
        patient.medication_manage_flag = True
        patient.medication_noti_flag = True

        data = dict()
        medication_noti_time = self.data.get('noti_time')
        if medication_noti_time:
            time = json.loads(medication_noti_time)['value']
            next_undefined_number = patient.next_undefined_medication_noti_time_number()

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
            response.add_simple_text(text="모든 회차 알림 설정을 마쳤습니다.\n[설정한 시간]\n%s" % time_list)
            response.add_simple_text(text="이대로 복약 알림을 설정할까요?")
            response.set_quick_replies_yes_or_no(
                block_id_for_yes="5db312bd8192ac000115f9ac",  # (블록) 06 치료 관리 재설정_알람 설정 완료
                block_id_for_no="5da549a6ffa7480001daf819",  # (블록) 01-1 치료 관리 설정_복약 관리 취소
                message_text_for_no="아니요")

            return response.get_response_200()
        else:
            time = time.split(':')[0] + '시 ' + time.split(':')[1] + '분'
            response.add_simple_text(text=f"{time}을 입력하셨어요.\n다음 회차를 설정하시려면 '예'를 눌러주세요.")
            response.set_quick_replies_yes_or_no(
                block_id_for_yes="5db312958192ac000115f9a5")  # (블록) 04 치료 관리 재설정_복약 알림 질문

            return response.get_response_200()


class PatientMedicationNotiReset(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()

        patient.reset_medication()
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        response.add_simple_text(text="복약 알림 설정을 취소했습니다.\n다시 설정할까요?")
        response.set_quick_replies_yes_or_no(
            block_id_for_yes="5da5e59ab617ea00012b43ee")  # (블록) 02 치료 관리 설정_복약횟수

        return response.get_response_200()


class PatientMedicationRestart(KakaoResponseAPI):
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

        if patient.medication_manage_flag:
            response.add_simple_text('안녕하세요 콜로크만입니다.\n지난 번, 복약 관리를 설정한 적이 있습니다.\n다시 설정할까요?')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5db30f398192ac000115f9a0',  # (블록) 02 치료 관리 재설정_복약횟수 확인
                block_id_for_no='5da549bcffa7480001daf821'  # (블록) 치료 관리 설정_시작하기 처음으로
            )
            response.add_context(name='복약관리재시작', params={'daily_medication_count': patient.daily_medication_count})
        else:
            response.add_simple_text('설정된 복약 관리가 없습니다.\n복약 관리를 새로 설정하러 가볼까요?')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5d9d8f74b617ea00012b14c6',  # (블록) 01 치료 관리 설정_복약 관리 시작
                block_id_for_no='5da549bcffa7480001daf821'  # (블록) 치료 관리 설정_시작하기 처음으로
            )

        return response.get_response_200()
