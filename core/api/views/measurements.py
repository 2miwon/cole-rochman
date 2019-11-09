import datetime
import json

from core.api.serializers import MeasurementResultSerializer
from django.http import Http404

from core.api.serializers import PatientUpdateSerializer
from core.api.util.helper import KakaoResponseAPI


class PatientMeasurementEntrance(KakaoResponseAPI):
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
        if patient.measurement_manage_flag:
            response.add_simple_text(text='산소포화도 관리를 설정한 적이 있습니다. 다시 설정할까요?')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5dc708cdffa74800014107a8',  # (블록) 02 건강재설정_알림횟수 확인
                block_id_for_no='5dc6d5d3b617ea0001798e2b',  # (블록) 01-2 건강재설정_취소
                message_text_for_yes='네, 설정할게요!', message_text_for_no='아니요, 괜찮아요!'
            )
            response.add_context(name='건강관리재설정', params={'daily_measurement_count': patient.daily_measurement_count})
        else:
            response.add_simple_text(text='산소포화도 관리를 시작하시겠습니까?')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5dbfa982b617ea000165eeee',  # (블록) 01-1 건강관리_횟수
                block_id_for_no='5dbfa931ffa748000115199e',  # (블록) 01-2 건강관리_취소
                message_text_for_yes='네, 시작할께요', message_text_for_no='아니요, 괜찮아요!'
            )

        return response.get_response_200()


class PatientMeasurementNotiTimeQuestion(KakaoResponseAPI):
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
        patient.measurement_noti_flag = True
        patient.save()
        if self.data.get('reset_measurement_noti_time') == 'true':
            patient.reset_measurement_noti_time()

        if not patient.need_measurement_noti_time_set() and len(patient.measurement_noti_time_list()) != 0:
            time_list = ','.join([x.strftime('%H시 %M분') for x in patient.measurement_noti_time_list()])

            message = f"이미 모든 회차 알림 설정을 마쳤습니다.\n[설정한 시간]\n{time_list}"
            response.add_simple_text(text=message)
            response.add_simple_text(text='산소포화도 확인 알림을 모두 재설정하시겠어요?')

            response.set_quick_replies_yes_or_no(block_id_for_yes='5dc708cdffa74800014107a8')  # (블록) 02 건강재설정_알림횟수 확인
        else:
            next_undefined_number = patient.next_undefined_measurement_noti_time_number()
            message = f'{next_undefined_number:d}회차 산소포화도 확인 알림을 설정할까요?'
            response.add_simple_text(text=message)
            if self.request.query_params.get('restart') == 'true':
                response.set_quick_replies_yes_or_no(
                    block_id_for_yes='5dc709c38192ac0001c5d9cb')  # (블록) 05 건강재설정_알림 시간대
            else:
                response.set_quick_replies_yes_or_no(
                    block_id_for_yes='5dbfaec792690d0001e8805d')  # (블록) 02-2 건강관리_산소포화도 알림 시간대

        return response.get_response_200()


class PatientMeasurementNotiSetTime(KakaoResponseAPI):
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
        patient.measurement_manage_flag = True
        patient.measurement_noti_flag = True

        data = dict()
        measurement_noti_time = self.data.get('noti_time')
        if measurement_noti_time:
            time = json.loads(measurement_noti_time)['value']
            next_undefined_number = patient.next_undefined_measurement_noti_time_number()

            if next_undefined_number:
                field_name = 'measurement_noti_time_%d' % next_undefined_number
                data[field_name] = time

        serializer = self.get_serializer(patient, data=data, partial=True)
        if not serializer.is_valid():
            response.add_simple_text(text='알 수 없는 오류가 발생했습니다. 입력값이 잘못 되었습니다.')
            return response.get_response_200()

        if not request.query_params.get('test'):
            serializer.save()

        patient.refresh_from_db()

        # check patient doesn't need measurement noti time set.
        if not patient.need_measurement_noti_time_set() and len(patient.measurement_noti_time_list()) != 0:
            time_list = ', '.join([x.strftime('%H시 %M분') for x in patient.measurement_noti_time_list()])
            response.add_simple_text(text='모든 회차 알림 설정을 마쳤습니다.\n[설정한 시간]\n%s' % time_list)
            response.add_simple_text(text='이대로 산소포화도 확인 알림을 설정할까요?')
            if self.request.query_params.get('restart') == 'true':
                response.set_quick_replies_yes_or_no(
                    block_id_for_yes='5dc709d48192ac0001c5d9cd',  # (블록) 06 건강재설정_알림 설정 완료
                    block_id_for_no='5dc72e60ffa74800014107c6',  # (블록) 건강관리_정보 리셋
                    message_text_for_no="아니요, 취소할게요")
            else:
                response.set_quick_replies_yes_or_no(
                    block_id_for_yes='5dbfb1ee8192ac00016aa32b',  # (블록) 03 건강관리_알람 설정 완료
                    block_id_for_no='5dc72e60ffa74800014107c6',  # (블록) 건강관리_정보 리셋
                    message_text_for_no="아니요, 취소할게요")

            return response.get_response_200()
        else:
            time = time.split(':')[0] + '시 ' + time.split(':')[1] + '분'
            response.add_simple_text(text=f'{time}을 입력하셨어요.\n다음 회차를 설정하시려면 \'예\'를 눌러주세요.')
            if self.request.query_params.get('restart') == 'true':
                response.set_quick_replies_yes_or_no(
                    block_id_for_yes='5dc7097affa74800014107ac')  # (블록) 04 건강재설정_알림 설정 질문
            else:
                response.set_quick_replies_yes_or_no(
                    block_id_for_yes='5dbfaeaf92690d0001e8805b')  # (블록) 02-1 건강관리_산소포화도 알림 시작

            return response.get_response_200()


class PatientMeasurementRestart(KakaoResponseAPI):
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

        response.add_simple_text('산소포화도 관리를 설정한 적이 있습니다.\n다시 설정할까요?')
        response.set_quick_replies_yes_or_no(
            block_id_for_yes='5dc708cdffa74800014107a8',  # (블록) 02 건강재설정_알림횟수 확인
            block_id_for_no='5dc6d5d3b617ea0001798e2b'  # (블록) 01-2 건강재설정_취소
        )

        return response.get_response_200()


class PatientMeasurementNotiReset(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()
        patient.reset_measurement()
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)
        return response.get_response_200()


class MeasurementResultCreate(KakaoResponseAPI):
    serializer_class = MeasurementResultSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()
        response = self.build_response(response_type=self.RESPONSE_SKILL)
        data = {
            'patient': patient.id,
            'oxygen_saturation': self.data.get('oxygen_saturation'),
            'measured_at': datetime.datetime.today().astimezone().strftime(self.DATETIME_STRPTIME_FORMAT)
        }
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return response.get_response_200()

        response.add_simple_text(text='알 수 없는 오류가 발생하였습니다')
        return response.get_response_200()
