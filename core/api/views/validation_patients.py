import re

from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView

from core.api.serializers import PatientCreateSerializer
from core.api.util.response_builder import ResponseBuilder


class ValidatePatientNickname(APIView):
    def post(self, request, *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        nickname = request.data.get('value').get('origin')

        if nickname:
            regex = re.compile(r'[a-zA-Z0-9ㄱ-힣]{1,10}')
            matched = re.search(regex, nickname)
            if matched:
                response.validation_success(value=matched.group())
                return response.get_response_200()

        response.validation_fail()
        return response.get_response_400()


class ValidatePatientCode(CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        value = request.data['value']['origin']
        regex = re.compile(r'[a-zA-Z]\d{11}')
        matched = re.search(regex, value)

        if not matched:
            response.validation_fail(message="유효하지 않은 코드입니다.")
            return response.get_response_400()

        qs = self.get_queryset()
        qs = qs.filter(code=matched.group().upper())
        if qs.exists():
            response.validation_fail(message="이미 등록된 코드입니다.")
            return response.get_response_400()

        response.validation_success(value=matched.group().upper())
        return response.get_response_200()
