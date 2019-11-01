import json

from django.http import Http404
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from core.api.serializers import TestSerializer, PatientCreateSerializer, PatientUpdateSerializer
from core.api.util.helper import KakaoResponseAPI

import logging

from core.api.util.response_builder import ResponseBuilder

logger = logging.getLogger(__name__)


class TestView(CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        serializer = TestSerializer(data={'data': request.data})
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)

        if serializer.is_valid():
            serializer.save()
            response.validation_success(value=serializer.validated_data)

            return response.get_response_200()

        response.validation_fail(value=serializer.validated_data)
        return response.get_response_400()


class PatientCreate(KakaoResponseAPI, CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        self.parse_kakao_user_id()
        self.parse_patient_code()

        data = dict()
        data['kakao_user_id'] = self.kakao_user_id
        data['code'] = self.patient_code

        nickname = self.detail_params.get('nickname')
        if nickname:
            data['nickname'] = json.loads(nickname)['value']

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
                date_time_dict = json.loads(value)
                data[key] = date_time_dict['date'] + " " + date_time_dict['time']
            elif 'time' in key:
                time_dict = json.loads(value)
                data[key] = time_dict['time']

        serializer = self.get_serializer(patient, data=data, partial=True)
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
