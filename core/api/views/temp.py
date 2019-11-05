from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from core.api.serializers import PatientCreateSerializer
from core.api.util.helper import KakaoResponseAPI


class TempPatientDestroy(KakaoResponseAPI):
    serializer_class = PatientCreateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = self.build_response(response_type=self.RESPONSE_SKILL)

        self.preprocess(request)
        self.parse_kakao_user_id()
        self.parse_patient_code()

        try:
            patient = self.get_object_by_kakao_user_id()
            patient_code = patient.code
            patient.delete()

            response.add_simple_text(text='삭제 되었습니다.\n환자코드 %s' % patient_code)
            return response.get_response_200()
        except Http404:
            response.add_simple_text(text='계정 등록이 되어 있지 않습니다.')
            return response.get_response_200()
