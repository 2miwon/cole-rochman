from django.http import Http404

from core.api.serializers import PatientUpdateSerializer
from core.api.util.helper import KakaoResponseAPI


class HealthManangementEntrance(KakaoResponseAPI):
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
        if patient.health_manage_flag:
            response.add_simple_text(text='산소포화도 관리를 설정한 적이 있습니다. 다시 설정할까요?')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5dc6d54fffa7480001410748',  # (블록) 01-1 건강재설정_재설정 시작
                block_id_for_no='5dc6d5d3b617ea0001798e2b',  # (블록) 01-2 건강재설정_취소
                message_text_for_yes='네, 설정할께요!', message_text_for_no='아니요, 괜찮아요!'
            )
        else:
            response.add_simple_text(text='산소포화도 관리를 시작하시겠습니까?')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5dbfa982b617ea000165eeee',  # (블록) 01-1 건강관리_횟수
                block_id_for_no='5dbfa931ffa748000115199e',  # (블록) 01-2 건강관리_취소
                message_text_for_yes='네, 시작할께요', message_text_for_no='5dbfa931ffa748000115199e'
            )

        return response.get_response_200()
