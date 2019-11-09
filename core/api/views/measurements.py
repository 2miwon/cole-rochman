import datetime

from django.http import Http404

from core.api.serializers import MeasurementResultSerializer
from core.api.util.helper import KakaoResponseAPI


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
