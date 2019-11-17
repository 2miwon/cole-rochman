from rest_framework.views import APIView

from core.api.util.response_builder import ResponseBuilder


class ValidateMeasurementResultOxygenSaturation(APIView):
    def post(self, request, *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        oxygen_saturation = request.data.get('value').get('origin')
        oxygen_saturation = int(oxygen_saturation)
        if 0 <= oxygen_saturation <= 100:
            response.set_validation_success(value=oxygen_saturation)
        else:
            response.set_validation_fail(message='0과 100 사이의 숫자를 입력하세요.')
        return response.get_response_200()
