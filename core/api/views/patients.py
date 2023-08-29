import json
import re
from datetime import date

from core.models import Patient,Profile
from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.serializers import PatientCreateSerializer, PatientUpdateSerializer
from core.api.util.helper import KakaoResponseAPI
from core.models import Profile

import logging

from core.api.util.response_builder import ResponseBuilder

logger = logging.getLogger(__name__)


# 계정이 등록되어 있는지 확인
# 없으면 계정 등록 시작으로 연결
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
                block_id_for_yes='63766ca8e748f261c9b19542',  # (블록) 02 계정등록_이름
                block_id_for_no='5d732d1b92690d0001813d45'  # (블록) Generic_시작하기 처음으로
            )
        else:
            response.add_simple_text(text='이미 계정이 등록되어 있습니다.\n계정 설정을 변경하시겠어요?')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='6350f6847e018a638ec9d73a',  # (블록) 카드_사용자 정보 변경
                block_id_for_no='5d732d1b92690d0001813d45'  # (블록) Generic_시작하기 처음으로
            )

        return response.get_response_200()


# 계정 등록 시작
# 환자 정보를 입력받음
class PatientCreate(KakaoResponseAPI, CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = self.build_response(response_type=self.RESPONSE_SKILL)

        self.preprocess(request)
        self.parse_kakao_user_id()
        self.parse_patient_code()        
        # self.parse_detail_params(self)

        if request.query_params.get('test'):
            hospital_code = "001"
        else:
            hospital_code = self.patient_code[:4]

        self.data['hospital'] = hospital_code
        name = self.data.get('name')
        birth = self.data.get('birth')
        gender = self.data.get('gender')
        phone_number = self.data.get('phone_number')
        nick_name = self.data.get('nickname')
        patient_code = self.data.get('patient_code')
        self.data['code'] = patient_code
        password = self.data.get('password')
        email = self.data.get('email')
        # user, _ = User.objects.get_or_create(username=patient_code, password=password, email=email)
        user = User.objects.create_user(patient_code,email,password)

        nickname = self.data.get('nickname')
        profile = Profile()
        profile.user = user
        profile.nickname = nickname
        profile.save()

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

            print(serializer.errors)
            response.add_simple_text(text='알 수 없는 오류가 발생했습니다.')
            response.set_quick_replies_yes_or_no()
            return response.get_response_200()

        if not request.query_params.get('test'):
            serializer.save()

        response.add_simple_text(text='결핵 치료 시작 날짜를 알고 계신가요?')
        response.set_quick_replies_yes_or_no(
                block_id_for_yes='5dc03c9bb617ea000165f4ae',  # (블록) 09-1 계정등록_치료 시작일 입력
                block_id_for_no='5dba743b92690d000164fa35',  # (블록) 09-2 계정등록_치료 시작일 모름
                message_text_for_yes='네', message_text_for_no='아니요'
            )
        return response.get_response_200()


# 환자정보 변경
class PatientUpdate(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
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
                try:
                    data[key] = value.strip('회')
                except AttributeError:
                    data[key] = value['value'].strip('회')
            elif 'medication_count' in key:
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
        
        if self.data.get('phone_number'):
            data['phone_number'] = self.data.get('phone_number')
        
        if self.data.get('birth'):
            data['birth'] = self.data.get('birth')

        if self.data.get('gender'):
            data['gender'] = self.data.get('gender')

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


# 환자정보 출력 (현재 사용 안 함)
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


# 환자의 외출가능여부 출력
class PatientSafeOut(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()
    
    def post(self, request, *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return response.get_response_200()

        if (patient.safeout == True):
            response.add_simple_text(text='현재 %s님은 사람을 만났을 때 전염성이 없습니다. 외출하셔도 괜찮습니다.' % patient.nickname)
        else:
            response.add_simple_text(text='현재 %s님은 아직은 외출을 피하셔야 합니다.' % patient.nickname)
        response.add_simple_text(text="자세한 정보를 위해서는 '결핵 정보'의 '결핵 치료'의 '결핵인데 외출해도 되나요?' 항목을 참고해 주세요.")
        response.add_quick_reply(
            action='block', label='이전으로 되돌아가기',
            block_id='63362c8a908af256004f3ac1'  # (블록) 카드_치료정보 환자용료
        )
        response.add_quick_reply(
            action='block', label='처음으로',
            block_id='5d732d1b92690d0001813d45'  # (블록) Generic_시작하기 처음으로
        )

        return response.get_response_200()


# 환자 몸무게 입력
class PatientWeight(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()
    
    def post(self, request, *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return response.get_response_200()

        weight = self.data.get('weight')
        patient.weight = float(weight)
        patient.save()
        
        return response.get_response_200()


# 환자 시력 입력
class PatientVision(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()
    
    def post(self, request, *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return response.get_response_200()

        vision_left = self.data.get('vision_left')
        vision_right = self.data.get('vision_right')
        patient.vision_left = float(vision_left)
        patient.vision_right = float(vision_right)
        patient.save()
        
        return response.get_response_200()


# 환자코드 출력
class PatientCodePrint(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()
    
    def post(self, request, *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=KakaoResponseAPI.RESPONSE_SKILL)

        try:
            patient = self.get_object_by_kakao_user_id()
            response.add_simple_text(text='사용자의 환자코드는 %s입니다.' % patient.code) 
            response.add_quick_reply(
        	    action='block', label='이전으로 되돌아가기',
        	    block_id='63627380978c6d37b652ac54'  # (블록) 카드_비밀번호 환자코드 찾기
            )
            response.add_quick_reply(
	            action='block', label='처음으로',
	            block_id='5d732d1b92690d0001813d45'  # (블록) Generic_시작하기 처음으로
            )
        except Http404:
            response.add_simple_text(text='계정등록을 먼저 해주십시오')
            response.add_quick_reply(
                action='block', label='계정등록 하러가기',
                block_id='630b0260f395392e2cfb8766'  # (블록) 00 계정등록_환자본인용or보호자용 선택
            )
#            return response.get_response_200()

#        if patient.code:
#            response.add_simple_text(text='사용자의 환자코드는 %s입니다.' % patient.code)
#        else:
#            response.add_simple_text(text='사용자는 아직 환자코드를 등록하지 않았습니다.')
#        response.add_quick_reply(
#        	action='block', label='이전으로 되돌아가기',
#        	block_id='63627380978c6d37b652ac54'  # (블록) 카드_비밀번호 환자코드 찾기
#        )
#        response.add_quick_reply(
#	        action='block', label='처음으로',
#	        block_id='5d732d1b92690d0001813d45'  # (블록) Generic_시작하기 처음으로
#        )

        return response.get_response_200()

