import json
import re

from core.models import Patient
from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.serializers import GuardianCreateSerializer, PatientCreateSerializer, PatientUpdateSerializer,MeasurementResultSerializer
from core.api.util.helper import KakaoResponseAPI

import logging

from core.api.util.response_builder import ResponseBuilder
from core.models.guardian import Guardian
from core.models.medication_result import MedicationResult
import datetime


class GuardianCreateStart(KakaoResponseAPI):
    serializer_class = GuardianCreateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, *args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=self.RESPONSE_SKILL)

        try:
            self.get_guardian_by_kakao_user_id()
            register_need = False
        except Http404:
            register_need = True

        if register_need:
            response.add_simple_text(text='보호자 계정을 등록하시겠습니까?\n보호자 계정을 등록해주시면\n환자분의 복약 여부를\n확인하실 수 있습니다.')
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='63918a8e698d3816872a7772',  # (블록) 02 보호자등록_환자확인
                block_id_for_no='5d732d1b92690d0001813d45'  # (블록) Generic_시>작하기 처음으로
            )
        else:
            response.add_simple_text(text='이미 보호자 계정이 등록되어 있습니다.')

        return response.get_response_200()


class GuardianCreate(KakaoResponseAPI, CreateAPIView):
    serializer_class = GuardianCreateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = self.build_response(response_type=self.RESPONSE_SKILL)
    
        self.preprocess(request)
        self.parse_kakao_user_id()
        
        name = self.data.get('patient_name')
        code = self.data.get('patient_code')
        try:
            patient = Patient.objects.get(name = name, code = code)
        except:
            response.add_simple_text(text='일치하는 환자가 없습니다.\n 입력하신 환자의 정보가 맞는지 다시 확인해주세요.')
            return response.get_response_400()
        self.data['patient_set'] = patient.pk
        serializer = self.get_serializer(data=self.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.query_params.get('test'):
            serializer.save()
                 
        return response.get_response_200()


class GuardianPhone(KakaoResponseAPI):
    serializer_class = PatientUpdateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = self.build_response(response_type=self.RESPONSE_SKILL)
        
        self.preprocess(request)
        try:
            guardian = self.get_guardian_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()
        
        guardian.phone_number = self.data.get('phone_number')
        guardian.save()
        
        return response.get_response_200()


#class GuardianCreate(KakaoResponseAPI, CreateAPIView):
#    serializer_class = GuardianCreateSerializer
#    model_class = serializer_class.Meta.model
#    queryset = model_class.objects.all()
#
#    def post(self, request, format='json', *args, **kwargs):
#        response = self.build_response(response_type=self.RESPONSE_SKILL)
#    
#        self.preprocess(request)
#        self.parse_kakao_user_id()
#        
##        # self.parse_patient_code 함수를 대신하여 직접 작성
##        code = self.params.get('patient_code')
##        code = code or self.detail_params.get('patient_code')
##        self.data.update({'code': code})
#
#        name = self.data.get('patient_name')
#        code = self.data.get('patient_code')
##        username = "(보호자)" + str(self.patient_code) 
#        try:
#            patient = Patient.objects.get(name = name, code = code)
#        except:
#            response.add_simple_text(text='일치하는 환자가 없습니다.\n 입력하신 환자의 정보가 맞는지 다시 확인해주세요.')
#            return response.get_response_400()
##        patient,_ = Patient.objects.get_or_create(code = code)
#        self.data['patient_set'] = patient.pk
#
#
##        if self.data['patient_code']:
##            del self.data['patient_code']
#
#        data = {
#            'code': code,
#            'kakao_user_id':self.data['kakao_user_id'],
#            'patient_set': patient.pk
#        }
#        print(data)
#        try:
#            guardian = Guardian.objects.get(code=str(code),patient_set=patient, kakao_user_id = self.data['kakao_user_id'])
#            print(guardian)
#        except:
#            register_need = True
#        if register_need:
#           print("계정 등록이 필요합니다")
#           guardian = Guardian()
#           guardian.code = str(code)
#           guardian.patient_set = patient
#           guardian.kakao_user_id = self.data['kakao_user_id']
#           guardian.save()
#      
# 
#         
# 
#        response.add_simple_text(text='계정이 성공적으로 등록되었습니다!👍\n결핵 치료 관리를 하시려면 아래 버튼을 눌러주십시오!')
#        response.add_simple_text(text='해당 환자분 복약 여부 확인하시겠습니까?')
#        response.set_quick_replies_yes_or_no(
#                block_id_for_yes='631c154e8142be671392b107',  # (블록) 01 계정관리_시작
#                block_id_for_no='5d732d1b92690d0001813d45'  # (블록) Generic_시작하기 처음으로
#            )
#        return response.get_response_200()

class GuardianCheckPatientMedication(KakaoResponseAPI):
    serializer_class = MeasurementResultSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request,format='json' ,*args, **kwargs):
        self.preprocess(request)
        response = self.build_response(response_type=self.RESPONSE_SKILL)

        try:
            self.parse_kakao_user_id()
            kakao_user_id = self.kakao_user_id
            guardian = Guardian.objects.get(kakao_user_id = kakao_user_id)
        except:
            response.add_simple_text("보호자만 조회 가능합니다. 보호자용 계정을 만드시겠습니까?")
            response.set_quick_replies_yes_or_no(
                block_id_for_yes='63919b29698d3816872a786d',  # 보호자 등록_시작
                block_id_for_no='5d732d1b92690d0001813d45',  # 처음으로 돌아가기
                message_text_for_yes='네, 설정할게요.', message_text_for_no='아니요, 괜찮아요.'
            )
            return response.get_response_200()

        # patient = Patient.objects.get(code = guardian.code)
        patient = guardian.patient_set
        print(patient.code)
        dailyresult=MedicationResult.objects.filter(patient__code__contains=patient.code, date = str(datetime.date.today()))
    
        if dailyresult:
            for i in dailyresult:
                if i.status == "SUCCESS":
                    text = '환자분은 복약을'
                    text += str(i.medication_time)[:-3]
                    text += '에 완료하셨습니다'
                    response.add_simple_text(text=text)
                elif i.status == "SIDE_EFFECT":
                    text = '환자께서 복약하셨으나 부작용이 있었습니다.\n'
                    text += '증상: '
                    text += str(i.symptom_name)
                    response.add_simple_text(text=text)
                else:
                    response.add_simple_text("환자꼐서 복약을 하지 않으셨습니다!!")
            return response.get_response_200()
        else:
            response.add_simple_text("환자분은 오늘 복약을 하지 않으셨습니다.")

        return response.get_response_200()
 
 
 
 
 
 
 
 
 
         
