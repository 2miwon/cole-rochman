from rest_framework.views import APIView

from core.api.util.response_builder import ResponseBuilder


class ResponseAlwaysOK(APIView):
    """
    되묻기 질문에서 응답을 받긴 해야 하지만, 응답을 검증하거나 저장할 필요가 없을때 사용합니다.
    """
    def post(self, request, *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.SKILL)
        return response.get_response_200()
