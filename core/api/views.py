import copy
import datetime
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
            elif 'count' in key:
                try:
                    params[key] = value.strip('회')
                except AttributeError:
                    params[key] = value['value'].strip('회')
            elif 'date_time' in key:
                date_time_dict = json.loads(value)
                params[key] = date_time_dict['date'] + " " + date_time_dict['time']
            elif 'time' in key:
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

        patient.medication_manage_flag = True
        patient.medication_noti_flag = True
        patient.save()

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
            times_str = ''

            for index, time in enumerate(patient.medication_noti_time_list()):
                times_str += '%d회차 알람 시간은 %s\n' % (index + 1, time.strftime('%H시 %M분'))

            times_str += '입니다.'

            response = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": "모든 회차 알림 설정을 마쳤습니다.\n%s" % times_str
                            }
                        },
                        {
                            "simpleText": {
                                "text": "이대로 복약 알람을 설정할까요?"
                            }
                        }
                    ],
                    "quickReplies": [
                        {
                            "action": "block",
                            "label": "예",
                            "blockId": "5da5ac8fb617ea00012b4363"  # (블록) 06 치료 관리 설정_알람 설정 완료
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

        params = dict()
        medication_noti_time = self.data.get('noti_time')
        if medication_noti_time:
            time_dict = json.loads(medication_noti_time)
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
            time_list = ', '.join([x.strftime('%H시 %M분') for x in patient.medication_noti_time_list()])
            response = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": "모든 회차 알림 설정을 마쳤습니다.\n[설정한 시간]\n%s" % time_list
                            }
                        },
                        {
                            "simpleText": {
                                "text": "내원 관리를 시작할까요?"
                            }
                        }
                    ],
                    "quickReplies": [
                        {
                            "action": "block",
                            "label": "예",
                            "blockId": "5d9df31692690d0001a458e6"  # (블록) 02 치료 관리 설정_내원 예정일 확인
                        #     TODO 퇴원환자의 경우 내원관리로 가면 안됨
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
                        "action": "block",
                        "label": "예",
                        # "messageText": "예",
                        "blockId": "5da5eac292690d0001a489e4"  # (블록) 03 치료 관리 설정_복약 알림 시간
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


class PatientMedicationNotiReset(KakaoResponseAPI):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        patient = self.get_object_by_kakao_user_id()
        patient.reset_medication_noti()
        response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "복약 알람 설정을 취소했습니다.\n다시 설정할까요?"
                        }
                    }
                ],
                "quickReplies": [
                    {
                        "action": "block",
                        "label": "예",
                        "blockId": "5da5e59ab617ea00012b43ee"  # (블록) 02 치료 관리 설정_복약횟수
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


class PatientVisitTimeBefore(KakaoResponseAPI):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        patient = self.get_object_by_kakao_user_id()

        seconds = self.data['visit_notification_before']  # 초 단위의 integer
        seconds = int(seconds)
        serializer = self.get_serializer(patient, data={'visit_notification_before': seconds}, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.query_params.get('test'):
            serializer.save()

        timedelta = datetime.timedelta(seconds=seconds)
        time_before_verbose = ''

        timedelta_hours = seconds // (60 * 60)
        timedelta_minutes = (seconds // 60) - (timedelta_hours * 60)

        if timedelta.days:
            time_before_verbose += '%d일 ' % timedelta.days
        if not timedelta_hours == 0:
            time_before_verbose += '%d시간 ' % timedelta_hours
        if not timedelta_minutes == 0:
            time_before_verbose += '%d분 ' % timedelta_minutes

        response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "내원 시간 %s 전에 알람을 드리겠습니다." % time_before_verbose.strip()
                        }
                    },
                    {
                        "simpleText": {
                            "text": "이대로 알람을 설정할까요?"
                        }
                    }
                ],
                "quickReplies": [
                    {
                        "action": "block",
                        "label": "예",
                        "blockId": "5d9df7978192ac0001156891"  # (블록) 05 치료 관리 설정_내원 관리 완료
                    },
                    {
                        "action": "block",
                        "label": "아니요",
                        "message": "아니요, 지금은 안 할래요.",
                        "blockId": "5d9df9368192ac00011568a9"  # (블록) 치료 관리 설정_내원 알람 종료
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


class ValidateTimeBefore(KakaoResponseAPI):
    def post(self, request, format='json', *args, **kwargs):
        SECONDS_FOR_MINUTE = 60
        SECONDS_FOR_HOUR = 60 * SECONDS_FOR_MINUTE
        SECONDS_FOR_DAY = 24 * SECONDS_FOR_HOUR

        value = request.data['value']['origin']

        minutes = re.search(r'\d{1,2}분', value)
        hours = re.search(r'\d{1,2}시', value)
        days = re.search(r'하루|이틀|\d+일', value)

        timedelta = 0

        if days:
            if days.group() == '하루':
                days_str = 1
            elif days.group() == '이틀':
                days_str = 2
            else:
                days_str = days.group().strip('일')
            timedelta += int(days_str) * SECONDS_FOR_DAY

        elif minutes and hours:
            minutes_str = minutes.group().strip('분')
            hours_str = hours.group().strip('시')
            timedelta += int(hours_str) * SECONDS_FOR_HOUR + int(minutes_str) * SECONDS_FOR_MINUTE

        elif minutes:
            minutes_str = minutes.group().strip('분')
            timedelta += int(minutes_str) * SECONDS_FOR_MINUTE

        elif hours:
            hours_str = hours.group().strip('시')
            timedelta += int(hours_str) * SECONDS_FOR_HOUR

        else:
            response_data = {
                "status": "FAIL"
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            "status": "SUCCESS",
            "value": timedelta
        }
        return Response(response_data, status=status.HTTP_200_OK)
