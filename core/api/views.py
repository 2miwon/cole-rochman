import copy
import json

from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response

from core.api.util.helper import KakaoResponseAPI
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


class PatientUpdate(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = PatientUpdateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        params = self.data
        patient = self.get_object_by_kakao_user_id()

        for key, value in params.items():
            if 'flag' in key:
                if value == '예' or 'true':
                    params[key] = True
                elif value == '아니요' or '아니오' or 'false':
                    params[key] = False

            if 'count' in key:
                params[key] = value.strip('회')

            if 'time' in key:
                time_dict = json.loads(value)
                params[key] = time_dict['time']

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
        return Response(response, status=status.HTTP_200_OK)


class PatientMedicationNotiTimeStart(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        patient = self.get_object_by_kakao_user_id()

        if not patient.has_undefined_noti_time():
            time_list = ','.join([x.strftime('%H시 %M분') for x in patient.medication_noti_time_list()])
            # TODO response = KakaoResponseAPI.build_response() 구현. 코드량 줄이기
            response = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": f"이미 모든 회차 알림 설정을 마쳤습니다.\n[설정한 시간]\n{time_list}"
                            }
                        }
                    ]
                }
            }
            # TODO 다음 액션 없음
            # TODO-2 시간 재설정할건지 물어보면 좋을 듯
            return Response(response, status=status.HTTP_200_OK)

        next_undefined_number = patient.next_undefined_noti_time_number()

        message = f'{next_undefined_number:d}회차 복약을 몇 시에 해야 하나요?\n(\'오전 몇 시\', 또는 \'오후 몇 시\'로 입력해주세요)\n예) 오후 1시'

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


class PatientMedicationNotiSetTime(KakaoResponseAPI):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        patient = self.get_object_by_kakao_user_id()

        if not patient.has_undefined_noti_time():  # TODO has_undefined_noti_time() 로직에 버그있음. (엣지 케이스 확인 필요)
            time_list = ','.join([x.strftime('%H시 %M분') for x in patient.medication_noti_time_list()])
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
        medication_noti_time = self.data.get('noti_time')
        if medication_noti_time:
            time_dict = json.loads(medication_noti_time['value'])
            next_undefined_number = patient.next_undefined_noti_time_number()

            if next_undefined_number == 1:
                params['medication_noti_time_1'] = time_dict['time']
            elif next_undefined_number == 2:
                params['medication_noti_time_2'] = time_dict['time']
            elif next_undefined_number == 3:
                params['medication_noti_time_3'] = time_dict['time']
            elif next_undefined_number == 4:
                params['medication_noti_time_4'] = time_dict['time']
            elif next_undefined_number == 5:
                params['medication_noti_time_5'] = time_dict['time']

        serializer = self.get_serializer(patient, data=params, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.query_params.get('test'):
            serializer.save()

        patient.refresh_from_db()
        if not patient.has_undefined_noti_time():
            time_list = ','.join([x.strftime('%H시 %M분') for x in patient.medication_noti_time_list()])
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
                        # "messageText": "복약 알림 시간 설정 테스트",
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
