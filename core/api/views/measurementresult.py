from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from core.models import MeasurementResult
from django.utils import timezone

from core.api.serializers import PatientUpdateSerializer
from core.api.util.helper import KakaoResponseAPI


class MeasurementResultUpdate(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        try:
            patient=self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()
        oxygen_sat=request.data.get('actions').get('detailParams').get('oxygen_saturation').get('value')

        result=MeasurementResult(patient=patient,measured_at=timezone.now(),oxygen_saturation=oxygen_sat)
        result.save()

        response = {
            "version": "2.0",
            "data": {
                'nickname': patient.nickname
            }
        }
        return Response(response, status=status.HTTP_200_OK)
