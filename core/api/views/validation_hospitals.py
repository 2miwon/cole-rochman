import re

from rest_framework.views import APIView

from core.api.util.response_builder import ResponseBuilder
from core.models import Hospital


class ValidateHospitalCode(APIView):
    def post(self, request, *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        hospital_code = request.data.get('value').get('origin')
        regex = re.compile(r'\w\d{3}')

        if not hospital_code:
            response.validation_fail()
            return response.get_response_400()

        matched = re.search(regex, hospital_code)
        if not matched:
            response.validation_fail()
            return response.get_response_400()

        if not Hospital.objects.filter(code=matched.group()).exists():
            response.validation_fail(value=matched.group(), message='알 수 없는 병원 코드입니다. 다시 한 번 확인해주세요.')
            return response.get_response_404()

        response.validation_success(value=matched.group())
        return response.get_response_200()
