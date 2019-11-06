
from rest_framework.views import APIView


from core.api.util.response_builder import ResponseBuilder




class ValidateOxygenSaturation(APIView):
    def post(self, request, *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        oxygen_saturation = request.data.get('value').get('origin')
        try:
            if 0<=int(oxygen_saturation)<=100:
                response.validation_success(value=int(oxygen_saturation))
                return response.get_response_200()
        except:
            response.validation_fail()
            return response.get_response_400()

        response.validation_fail()
        return response.get_response_400()

