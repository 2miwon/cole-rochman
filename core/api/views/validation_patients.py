import re

from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView

from core.api.serializers import PatientCreateSerializer
from core.api.util.response_builder import ResponseBuilder
from core.models import Hospital


class ValidatePatientNickname_N02(APIView):
    def post(self, request, *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        nickname = request.data.get('value').get('origin')

        if nickname:
            regex = re.compile(r'[a-zA-Z0-9ㄱ-힣]{1,10}')
            matched = re.search(regex, nickname)
            if matched:
                response.set_validation_success(value=matched.group())
                return response.get_response_200()

        response.set_validation_fail()
        return response.get_response_400()

class ValidatePatientNickname(APIView):
    def post(self, request, *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        nickname = request.data.get('value').get('origin')

        if nickname:
            reg = "^[a-zA-Z0-9가-힣]{1,10}$"
            if bool(re.match(reg,nickname)):
#                print("Validation Success")
                response.set_validation_success(value=nickname)
                return response.get_response_200()

#        print("Validation Fail")
        response.set_validation_fail()
        return response.get_response_400()

class ValidatePatientCode(CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        value = request.data['value']['origin']
        regex = re.compile(r'[a-zA-Z]\d{11}')
        matched = re.search(regex, value)

        if not matched:
            response.set_validation_fail(message='유효하지 않은 코드입니다.')
            return response.get_response_400()

        patient_code = matched.group().upper()
        hospital_code = patient_code[:4]
        if not self.hospital_exists(hospital_code):
            response.set_validation_fail(message='유효하지 않은 코드입니다. 앞 3자리(병원코드)를 확인해주세요.')
            return response.get_response_400()

        response.set_validation_success(value=patient_code)
        return response.get_response_200()

    @staticmethod
    def hospital_exists(code):
        return Hospital.objects.filter(code=code).exists()



class ValidatePatientCode_N03(CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        value = request.data['value']['origin']
        reg = "^[a-zA-Z][0-9]{11}$"
        matched = re.search(regex, value)

#        print("stage1")
        if not bool(re.match(reg, value)):
            response.set_validation_fail(message='유효하지 않은 코드입니다.')
#            print("Error1")
            return response.get_response_400()

        patient_code = value().upper()
        hospital_code = patient_code[:4]
#        print("stage2")
        if not self.hospital_exists(hospital_code):
            response.set_validation_fail(message='유효하지 않은 코드입니다. 앞 3자리(병원코드)를 확인해주세요.')
#            print("Error2")
            return response.get_response_400()

#        print("Success1")
        response.set_validation_success(value=patient_code)
        return response.get_response_200()

    @staticmethod
    def hospital_exists(code):
#        print("stage3")
        return Hospital.objects.filter(code=code).exists()
