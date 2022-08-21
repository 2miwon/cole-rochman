import json
import re

from core.models import Patient
from django.contrib.auth.models import User
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


class PatientCreateStart(KakaoResponseAPI):
    serializer_class = PatientCreateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=self.RESPONSE_SKILL)

        try:
            self.get_object_by_kakao_user_id()
            register_need = False
        except Http404:
            register_need = True

        if register_need:
            response.add_simple_text(text='계정을 등록하시겠습니까?\n계정을 등록해주시면\n저와 함께 치료 관리와 건강관리를\n시작하실 수 있습니다.')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5dbfcfe892690d0001e882d8',  # (블록) 02 계정등록_별명 등록
                block_id_for_no='5d732d1b92690d0001813d45'  # (블록) Generic_시작하기 처음으로
            )
        else:
            response.add_simple_text(text='이미 계정이 등록되어 있습니다.\n계정 설정을 변경하시겠어요?')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5dbf9e1592690d0001e87f9f',  # (블록) 01 계정관리_시작
                block_id_for_no='5d732d1b92690d0001813d45'  # (블록) Generic_시작하기 처음으로
            )

        return response.get_response_200()


class PatientCreateStart_N01(KakaoResponseAPI):
    serializer_class = PatientCreateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=self.RESPONSE_SKILL)

        try:
            self.get_object_by_kakao_user_id()
            register_need = False
        except Http404:
            register_need = True

        if register_need:
            response.add_simple_text(text='계정을 등록하시겠습니까?\n계정을 등록해주시면\n저와 함께 치료 관리와 건강관리를\n시작하실 수 있습니다.')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='62c03ea99fdc7e48f2c16af9',  # (블록) 02 계정등록_별명 등록
                block_id_for_no='5d732d1b92690d0001813d45'  # (블록) Generic_시작하기 처음으로
            )
        else:
            response.add_simple_text(text='이미 계정이 등록되어 있습니다.\n계정 설정을 변경하시겠어요?')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='5dbf9e1592690d0001e87f9f',  # (블록) 01 계정관리_시작
                block_id_for_no='5d732d1b92690d0001813d45'  # (블록) Generic_시작하기 처음으로
            )

        return response.get_response_200()

class NicknameSkill(KakaoResponseAPI):
    def post(self, request, *args, **kwargs):
        response = self.build_response(response_type=self.RESPONSE_SKILL)
        nickname = request.data.get('actions').get('detailParams').get('nickname').get('value')

        if nickname:
            regex = re.compile(r'[a-zA-Z0-9ㄱ-힣]{1,10}')
            matched = re.search(regex, nickname)
            response.add_simple_text(text='%s를 입력받았습니다.' % nickname)
            if matched:
                response.add_simple_text(text='%s님 반갑습니다. 현재 결핵 치료를 위해서 병원에 다니시나요?' % nickname)
                response.set_quick_replies_yes_or_no(block_id_for_yes='TEXT')
            else:
                return self.build_response_fallback_404()
        else:
            return self.build_response_fallback_404()

        return response.get_response_200()


class PatientCreate(KakaoResponseAPI, CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = self.build_response(response_type=self.RESPONSE_SKILL)

        self.preprocess(request)
        self.parse_kakao_user_id()
        self.parse_patient_code()

        hospital_code = self.patient_code[:4]
        self.data['hospital'] = hospital_code
        user, _ = User.objects.get_or_create(username=hospital_code)
        self.data['user'] = user.pk

        serializer = self.get_serializer(data=self.data)
        if not serializer.is_valid():
            if any([error_detail.code == 'unique' for error_detail in serializer.errors.get('code') or []]):
                response.add_simple_text(text='이미 등록된 환자 코드입니다.\n다시 입력하시겠어요?')
                response.set_quick_replies_yes_or_no(
                    block_id_for_yes='5da3ed3392690d0001a475cb',  # (블록) 04 계정등록_환자 코드
                    block_id_for_no='5dc38fa2b617ea0001320fbd',  # (블록) 계정등록_취소
                )
                return response.get_response_200()

            response.add_simple_text(text='알 수 없는 오류가 발생했습니다.')
            response.set_quick_replies_yes_or_no()
            return response.get_response_200()

        if not request.query_params.get('test'):
            serializer.save()

        response.add_simple_text(text='계정이 성공적으로 등록되었습니다!👍\n결핵 치료 관리를 하시려면 아래 버튼을 눌러주십시오!')
        response.add_quick_reply(action='block', label='결핵 치료 관리 시작하기',
                                 block_id='5dba635892690d000164f9b2'  # (블록)  06 계정등록_결핵 치료 시작일 알고 있는지
                                 )
        return response.get_response_200()

class PatientCreate_N04(KakaoResponseAPI, CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = self.build_response(response_type=self.RESPONSE_SKILL)

        self.preprocess(request)
        self.parse_kakao_user_id()
#        print('before parse_patient_code()')
        self.parse_patient_code()
#        print('after parse_patient_code()')

        kakao_id = self.data.get('kakao_user_id')
#        print('kakao_id: ', kakao_id)
        nick = self.data.get('nickname')
#        print('nickname: ', nick)
        
        pat = self.data.get('code')
#        print('patient_code: ', pat)

        hospital_code = self.patient_code[:4]
#        print('hospital_code: ', hospital_code)

        self.data['hospital'] = hospital_code

        user, _ = User.objects.get_or_create(username=hospital_code)

        self.data['user'] = user.pk
        user_pk = self.data.get('user')
#        print('user_pk: ', user_pk)

#        print('PatientCreate 1st')

        serializer = self.get_serializer(data=self.data)
#        print('data: ', self.data)
#        patient = self.get_object(user_pk)
#        serializer = PatientCreateSerializer(patient, data=self.data)
#        print('serializer: ', serializer)
#        print('serializer.is_valid: ', serializer.is_valid())
#        print(serializer.errors)
        if not serializer.is_valid():
            if any([error_detail.code == 'unique' for error_detail in serializer.errors.get('code') or []]):
                response.add_simple_text(text='이미 등록된 환자 코드입니다.\n다시 입력하시겠어요?')
                response.set_quick_replies_yes_or_no(
                    block_id_for_yes='62c0423223b93f4440ce8a7d',  # (블록) 04 계정등록_환자 코드
                    block_id_for_no='5dc38fa2b617ea0001320fbd',  # (블록) 계정등록_취소
                )
                return response.get_response_200()

            response.add_simple_text(text='알 수 없는 오류가 발생했습니다.')
            response.set_quick_replies_yes_or_no()
            return response.get_response_200()

#        if not request.query_params.get('test'):
#            serializer.save()
        serializer.save()
#        print('After: serial save()')

        response.add_simple_text(text='계정이 성공적으로 등록되었습니다!👍\n결핵 치료 관리를 하시려면 아래 버튼을 눌러주십시오!')
        response.add_quick_reply(action='block', label='결핵 치료 관리 시작하기', block_id='62c12b8f50b23b1e3a6e2ea1')  # (블록)  06 계정등록_결핵 치료 시작일 알고 있는지
        return response.get_response_200()

class PatientUpdate(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        #print('At PatientUpdate Org 1st')
        self.preprocess(request)
        data = self.data
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()

        if self.data.get('reset_visit_noti'):
            patient.reset_visit()
            patient.visit_manage_flag = True
            patient.visit_notification_flag = True
            patient.save()

        if self.data.get('reset_medication_noti'):
            patient.reset_medication()
            patient.medication_manage_flag = True
            patient.medication_noti_flag = True
            patient.save()

        if self.data.get('reset_measurement_noti'):
            patient.reset_measurement()
            patient.measurement_manage_flag = True
            patient.measurement_noti_flag = True
            patient.save()

        for key, value in data.items():
            if 'flag' in key:
                if value == '예' or 'true':
                    data[key] = True
                elif value == '아니요' or '아니오' or 'false':
                    data[key] = False
            elif 'measurement_count' in key:
#                print('measurement count: ', value)
                try:
                    data[key] = value.strip('회')
                except AttributeError:
                    data[key] = value['value'].strip('회')
            elif 'medication_count' in key:
#                print('medication count: ', value)
                try:
                    data[key] = value.strip('회')
                except AttributeError:
                    data[key] = value['value'].strip('회')
            elif 'count' in key:
                try:
                    data[key] = value.strip('회')
                except AttributeError:
                    data[key] = value['value'].strip('회')
            elif 'date_time' in key:
                try:
                    date_time_dict = json.loads(value)
                except TypeError:
                    date_time_dict = value

                try:
                    data[key] = date_time_dict['date'] + " " + date_time_dict['time']
                except (TypeError, KeyError):
                    data[key] = date_time_dict['date'] + " " + date_time_dict['time']
            elif 'date' in key:
                try:
                    date_dict = json.loads(value)
                except TypeError:
                    date_dict = value

                try:
                    data[key] = date_dict['date']
                except (TypeError, KeyError):
                    data[key] = date_dict['value']
            elif 'time' in key:
                try:
                    time_dict = json.loads(value)
                except TypeError:
                    time_dict = value

                try:
                    data[key] = time_dict['time']
                except (TypeError, KeyError):
                    data[key] = time_dict['value']

        if self.data.get('patient_code'):
            data['code'] = self.data.get('patient_code')

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

class PatientUpdate_N05(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):

#        print('At PatientUpdate 1st')
        kakao_id = request.data.get('userRequest').get('user').get('id')
#        print('kakao_id: ', kakao_id)

        self.preprocess(request)
        queryset = Patient.objects.all()
        data = self.data

        nick = data.get('nickname')
#        print('nickname: ', nick)

        try:
#            print('After try:')
            patient = self.get_object_by_kakao_user_id()
        except Http404:
#            print('At PatientUpdate Http404')
            return self.build_response_fallback_404()
#        print('At PatientUpdate after except')

        if self.data.get('reset_visit_noti'):
            patient.reset_visit()
            patient.visit_manage_flag = True
            patient.visit_notification_flag = True
            patient.save()

        if self.data.get('reset_medication_noti'):
            patient.reset_medication()
            patient.medication_manage_flag = True
            patient.medication_noti_flag = True
            patient.save()

        if self.data.get('reset_measurement_noti'):
            patient.reset_measurement()
            patient.measurement_manage_flag = True
            patient.measurement_noti_flag = True
            patient.save()

        for key, value in data.items():
#            if 'nickname' in key:
#                print("nickname: " , value)
#                data[key] = value
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
                except TypeError:
                    date_time_dict = value

                try:
                    data[key] = date_time_dict['date'] + " " + date_time_dict['time']
                except (TypeError, KeyError):
                    data[key] = date_time_dict['date'] + " " + date_time_dict['time']
            elif 'date' in key:
                try:
                    date_dict = json.loads(value)
                except TypeError:
                    date_dict = value

                try:
                    data[key] = date_dict['date']
                except (TypeError, KeyError):
                    data[key] = date_dict['value']
            elif 'time' in key:
                try:
                    time_dict = json.loads(value)
                except TypeError:
                    time_dict = value

                try:
                    data[key] = time_dict['time']
                except (TypeError, KeyError):
                    data[key] = time_dict['value']

        if data.get('patient_code'):
            data['code'] = self.data.get('patient_code')

        serializer = self.get_serializer(patient, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#        print('At PatientUpdate before save')
        serializer.save()
        #if not request.query_params.get('test'):

        response = {
            "version": "2.0",
            "data": {
                'nickname': patient.nickname
            }
        }
        return Response(response, status=status.HTTP_200_OK)


class PatientInfo(KakaoResponseAPI):
    """
    환자의 정보를 응답합니다. 없으면 빈 문자열을 내려줍니다.
    """
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, *args, **kwargs):
        self.preprocess(request)
        response = ResponseBuilder(response_type=ResponseBuilder.SKILL)

        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            response.add_data('nickname', '')
            response.add_data('patient_code', '')
            return response.get_response_200()

        response.add_data('nickname', patient.nickname or '')
        response.add_data('patient_code', patient.code or '')
        return response.get_response_200()
