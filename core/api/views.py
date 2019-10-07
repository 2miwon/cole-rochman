from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import PatientSerializer, TestSerializer


class TestView(APIView):
    def post(self, request, format='json', *args, **kwargs):
        serializer = TestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "status": "SUCCESS",
                "value": "test data save complete",
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        response_data = {
            "status": "FAIL",
            "value": "test data save failed",
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class PatientCreate(CreateAPIView):
    serializer_class = PatientSerializer
    model_class = PatientSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        payload = dict()
        payload['kakao_user_id'] = request.data['userRequest']['user']['id']
        payload['code'] = request.data['action']['detailParams']['patient_code']['value']

        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
