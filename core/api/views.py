import json

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

        for key, value in params.items():
            if 'flag' in key:
                if value == '예' or 'true':
                    params[key] = True
                elif value == '아니요' or '아니오' or 'false':
                    params[key] = False

            if 'count' in key:
                params[key] = value.strip('회')

            if 'time' in key:
                params[key] = value['time']

        serializer = self.get_serializer(patient, data=params, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.query_params.get('test'):
            serializer.save()
        response = {
            "version": "2.0",
            "data": {
            }
        }
        # response = serializer.validated_data
        return Response(response, status=status.HTTP_200_OK)


class PatientMediacationNotiTimeStart(CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        kakao_user_id = request.data['userRequest']['user']['id']
        try:
            patient = self.queryset.get(kakao_user_id=kakao_user_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not patient.has_undefined_noti_time():
            time_list = ','.join([x.strftime('%H시 %i분') for x in patient.medication_noti_time_list()])
            response = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": "모든 회차 알림 설정을 마쳤습니다.\n[설정한 시간]\n%s" % time_list
                            }
                        }
                    ]
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        params = dict()
        params['kakao_user_id'] = kakao_user_id

        next_undefined_number = patient.next_undefined_noti_time_number()

        message = "%d회차 복약을 몇 시에 해야 하나요?\n('오전 몇 시', 또는 '오후 몇 시'로 입력해주세요)\n예) 오후 1시" % next_undefined_number

        response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": message
                        }
                    }
                ]
            }
        }
        return Response(response, status=status.HTTP_200_OK)


class PatientMediacationNotiSetTime(CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        kakao_user_id = request.data['userRequest']['user']['id']
        try:
            patient = self.queryset.get(kakao_user_id=kakao_user_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not patient.has_undefined_noti_time():
            time_list = ','.join([x.strftime('%H시 %i분') for x in patient.medication_noti_time_list()])
            response = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": "모든 회차 알림 설정을 마쳤습니다.\n[설정한 시간]\n%s" % time_list
                            }
                        }
                    ]
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        params = dict()
        next_undefined_number = patient.next_undefined_noti_time_number()
        field = ''
        if next_undefined_number == 1:
            field = 'medication_noti_time_1'
        elif next_undefined_number == 2:
            field = 'medication_noti_time_2'
        elif next_undefined_number == 3:
            field = 'medication_noti_time_3'
        elif next_undefined_number == 4:
            field = 'medication_noti_time_4'
        elif next_undefined_number == 5:
            field = 'medication_noti_time_5'

        medication_noti_time = request.data['action']['detailParams'].get('noti_time')
        if medication_noti_time:
            params[field] = medication_noti_time['value']
        params['kakao_user_id'] = kakao_user_id

        if next_undefined_number == 1:
            params['medication_noti_time_1'] = medication_noti_time
        elif next_undefined_number == 2:
            params['medication_noti_time_2'] = medication_noti_time
        elif next_undefined_number == 3:
            params['medication_noti_time_3'] = medication_noti_time
        elif next_undefined_number == 4:
            params['medication_noti_time_4'] = medication_noti_time
        elif next_undefined_number == 5:
            params['medication_noti_time_5'] = medication_noti_time

        serializer = self.get_serializer(patient, data=params, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.query_params.get('test'):
            serializer.save()

        patient.refresh_from_db()
        if not patient.has_undefined_noti_time():
            time_list = ','.join([x.strftime('%H시 %i분') for x in patient.medication_noti_time_list()])
            response = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": "모든 회차 알림 설정을 마쳤습니다.\n[설정한 시간]\n%s" % time_list
                            }
                        }
                    ]
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "다음 회차를 설정하시려면 '예'를 눌러주세요."
                        }
                    }
                ],
                "quickReplies": [
                    {
                        "action": "message",
                        "label": "예",
                        "messageText": "예",
                        "blockId": "5da5eac292690d0001a489e4"
                    },
                    {
                        "action": "message",
                        "label": "아니요",
                        "messageText": "아니요"
                    }
                ]
            }
        }
        return Response(response, status=status.HTTP_200_OK)


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
