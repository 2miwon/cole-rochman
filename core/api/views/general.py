from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class ResponseAlwaysOK(APIView):
    """
    되묻기 질문에서 응답을 받긴 해야 하지만, 응답을 검증하거나 저장할 필요가 없을때 사용합니다.
    """
    def post(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
