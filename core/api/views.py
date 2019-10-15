from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response

from .serializers import PatientCreateSerializer, PatientUpdateSerializer, TestSerializer

import logging
import re

logger = logging.getLogger(__name__)


class TestView(CreateAPIView):
    def post(self, request, format='json', *args, **kwargs):
        serializer = TestSerializer(data={'data': request.data})

        if serializer.is_valid():
            serializer.save()
            response_data = {
                "status": "SUCCESS",
                "value": serializer.validated_data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        response_data = {
            "status": "FAIL",
            "value": serializer.validated_data
        }
        logger.error(serializer.data)
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class PatientCreate(CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        data = dict()
        data['kakao_user_id'] = request.data['userRequest']['user']['id']
        data['code'] = request.data['action']['params']['patient_code']

        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.query_params.get('test'):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        response = serializer.validated_data
        response['test'] = True
        return Response(response, status=status.HTTP_201_CREATED)


class PatientUpdate(GenericAPIView):
    serializer_class = PatientUpdateSerializer
    model_class = PatientUpdateSerializer.Meta.model
    queryset = model_class.objects.all()
    lookup_field = 'kakao_user_id'

    def post(self, request, *args, **kwargs):
        kakao_user_id = request.data['userRequest']['user']['id']
        try:
            patient = self.queryset.get(kakao_user_id=kakao_user_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        params = request.data['action']['params']
        params['kakao_user_id'] = kakao_user_id
        if 'patient_code' in params:
            params['code'] = params['patient_code']

        serializer = self.get_serializer(patient, data=params, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.query_params.get('test'):
            serializer.save()

        response = serializer.validated_data
        return Response(response, status=status.HTTP_204_NO_CONTENT)


class ValidatePatientCode(CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        value = request.data['value']['origin']
        regex = re.compile(r'[a-zA-Z]\d{11}')
        matched = re.search(regex, value)

        if not matched:
            response_data = {
                "status": "FAIL",
                "message": "유효하지 않은 코드입니다."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        qs = self.get_queryset()
        qs = qs.filter(code=matched.group().upper())
        if qs.exists():
            response_data = {
                "status": "FAIL",
                "message": "이미 등록된 코드입니다."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            "status": "SUCCESS",
            "value": matched.group().upper()
        }
        return Response(response_data, status=status.HTTP_200_OK)


class MediacationNotificationTest(CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "1회차 알림받을 시간을 선택해주세요."
                        }
                    }
                ],
                "quickReplies": [
                    {
                        "action": "message",
                        "label": "오후 1시",
                        "messageText": "1회차 알람으로 오후 1시에 알람을 설정합니다."
                    },
                    {
                        "action": "message",
                        "label": "오후 2시",
                        "messageText": "1회차 알람으로 오후 2시에 알람을 설정합니다."
                    },
                ]
            }
        }
        return Response(response, status=status.HTTP_200_OK)
