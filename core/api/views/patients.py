import json
import re

from django.http import Http404
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.serializers import PatientCreateSerializer, PatientUpdateSerializer
from core.api.util.helper import KakaoResponseAPI

import logging

from core.api.util.response_builder import ResponseBuilder

logger = logging.getLogger(__name__)


class NicknameSkill(APIView):

    def post(self, request, *args, **kwargs):
        self.response = ResponseBuilder(response_type=ResponseBuilder.SKILL)
        nickname = request.data.get('actions').get('detailParams').get('nickname').get('value')

        if nickname:
            regex = re.compile(r'[a-zA-Z0-9ㄱ-힣]{1,10}')
            matched = re.search(regex, nickname)
            self.response.add_simple_text(text='%s를 입력받았습니다.' % nickname)
            if matched:
                self.response.add_simple_text(text='%s님 반갑습니다. 현재 결핵 치료를 위해서 병원에 다니시나요?' % nickname)
                self.response.set_quick_replies_yes_or_no(block_id_for_yes='TEXT')
            else:
                self.build_fallback_response()
        else:
            self.build_fallback_response()

        return Response(self.response, status=status.HTTP_200_OK)


class PatientCreate(KakaoResponseAPI, CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = self.build_response(response_type=self.RESPONSE_SKILL)

        self.preprocess(request)
        self.parse_kakao_user_id()
        self.parse_patient_code()

        self.data['hospital'] = self.data['hospital_code']

        serializer = self.get_serializer(data=self.data)
        if serializer.is_valid():
            if not request.query_params.get('test'):
                serializer.save()
                return response.get_response_200()

            return response.get_response_200()
        else:
            response.add_simple_text(text='이미 등록된 계정입니다.')
            response.add_quick_reply(action='block', label='다음으로 진행하기',
                                     block_id='5dba635892690d000164f9b2')  # 06 계정등록_결핵 치료 시작일 알고 있는지
            return response.get_response_200()


class PatientUpdate(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = PatientUpdateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        data = self.data
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()

        for key, value in data.items():
            if 'flag' in key:
                if value == '예' or 'true':
                    data[key] = True
                elif value == '아니요' or '아니오' or 'false':
                    data[key] = False
            elif 'count' in key:
                try:
                    data[key] = value.strip('회')
                except AttributeError:
                    data[key] = value['value'].strip('회')
            elif 'date_time' in key:
                try:
                    date_time_dict = json.loads(value)
                    data[key] = date_time_dict['date'] + " " + date_time_dict['time']
                except TypeError or KeyError:
                    data[key] = value['date'] + " " + value['time']
            elif 'date' in key:
                try:
                    date_dict = json.loads(value)
                    data[key] = date_dict['date']
                except TypeError or KeyError:
                    data[key] = value['value']
            elif 'time' in key:
                try:
                    time_dict = json.loads(value)
                    data[key] = time_dict['time']
                except TypeError or KeyError:
                    data[key] = value['value']

        serializer = self.get_serializer(patient, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.query_params.get('test'):
            serializer.save()

        response = {
            "version": "2.0",
            "data": {
                'nickname': patient.nickname
            }
        }
        return Response(response, status=status.HTTP_200_OK)
