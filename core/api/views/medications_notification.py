import munch as munch
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.utils import json

from core.api.serializers import PatientUpdateSerializer

from core.api.util.helper import KakaoResponseAPI


class PastMedicationCheckChooseTime(KakaoResponseAPI):
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


