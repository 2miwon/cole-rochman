import re

from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView

from core.api.serializers import PatientCreateSerializer
from core.api.util.response_builder import ResponseBuilder
from core.models import Hospital
from core.models import Patient
import datetime

def check_initializing(response, value) -> bool:
    if value=='처음으로':
        response.set_validation_fail(message='처음으로 돌아가기 위해서는 "처음으로 돌아가기"라고 입력해주세요\n계정등록을 중간에 중지한 경우 계정이 등록되지 않습니다.\n\n')
        return False
    return True

class ValidatePatientName(CreateAPIView):
    serializeR_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, forrmat='json', *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        value = request.data['value']['origin']
        
        if check_initializing(response, value):
            response.set_validation_success(value=value)

        return response.get_response_200()



class ValidatePatientBirth(CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        value = request.data['value']['origin']
        
        if check_initializing(response, value):
            try:
                datetime.date.fromisoformat(value)
            except ValueError:
                response.set_validation_fail(message='정확하지않은 날짜 입력 값입니다.')
                return response.get_response_400()
            response.set_validation_success(value=value)

        return response.get_response_200()


class ValidatePatientGender(CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        value = request.data['value']['origin']
        
        if check_initializing(response, value):
            male = ["남성", "남자", "남", "male", "boy"]
            female = ["여성", "여자", "여", "female", "girl"]
            allowed = male + female
            if(value not in allowed):
                response.set_validation_fail(message='성별은 남성 또는 여성으로 입력해주세요.')
                return response.get_response_400()
            
            if(value in male):
                rst = "남성"
            if(value in female):
                rst = "여성"

            response.set_validation_success(value=rst)
        return response.get_response_200()



class ValidatePatientPhone(CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        value = request.data['value']['origin']
        
        if value=='처음으로':
            response.set_validation_fail(message='처음으로 돌아가기 위해서는 "처음으로 돌아가기"라고 입력해주세요\n계정등록을 중간에 중지한 경우 계정이 등록되지 않습니다.\n\n')
            return response.get_response_200()
        
        isInt = True
        try:
            int(value)
        except ValueError:
            isInt = False
        if not isInt:
            response.set_validation_fail(message='전화번호는 01012345678과 같은 형태로 입력해주세요.')
            return response.get_response_400()
        
        response.set_validation_success(value=value)
        return response.get_response_200()


class ValidatePatientNickname(APIView):
    def post(self, request, *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        nickname = request.data.get('value').get('origin')
        
        if nickname=='처음으로':
            response.set_validation_fail(message='처음으로 돌아가기 위해서는 "처음으로 돌아가기"라고 입력해주세요\n계정등록을 중간에 중지한 경우 계정이 등록되지 않습니다.\n\n')
            return response.get_response_200()

        if nickname:
            reg = "^[a-zA-Z0-9가-힣]{1,10}$"
            if bool(re.match(reg,nickname)):
                response.set_validation_success(value=nickname)
                return response.get_response_200()

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
        
        if value=='처음으로':
            response.set_validation_fail(message='처음으로 돌아가기 위해서는 "처음으로 돌아가기"라고 입력해주세요\n계정등록을 중간에 중지한 경우 계정이 등록되지 않습니다.\n\n')
            return response.get_response_200()

        if not matched:
            response.set_validation_fail(message='유효하지 않은 코드입니다.\n\n')
            return response.get_response_200()

        patient_code = matched.group().upper()
        hospital_code = patient_code[:4]
        if not self.hospital_exists(hospital_code):
            response.set_validation_fail(message='유효하지 않은 코드입니다. 앞 3자리(병원코드)를 확인해주세요.\n\n')
            return response.get_response_200()
        
        patients = Patient.objects.all()
        if any(patient_code == patient.code for patient in patients):
            response.set_validation_fail(message='이미 존재하는 코드입니다. 다른 코드를 입력해주세요.\n\n')
            return response.get_response_200()

        response.set_validation_success(value=patient_code)
        return response.get_response_200()

    @staticmethod
    def hospital_exists(code):
        return Hospital.objects.filter(code=code).exists()


class ValidatePatientPassword(CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        value = request.data['value']['origin']
        
        if value=='처음으로':
            response.set_validation_fail(message='처음으로 돌아가기 위해서는 "처음으로 돌아가기"라고 입력해주세요\n계정등록을 중간에 중지한 경우 계정이 등록되지 않습니다.\n\n')
            return response.get_response_200()

        if len(value) < 8:
            response.set_validation_fail(message='첫번째 조건을 다시 한 번 확인해주세요.\n\n')
            return response.get_response_200()

        if not value.isdigit():
            response.set_validation_fail(message='두번째 조건을 다시 한 번 확인해주세요.\n\n')
            return response.get_response_200()

        response.set_validation_success(value=value)
        return response.get_response_200()


class ValidatePatientWeight(CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        value = request.data['value']['origin']
        
        if value=='처음으로':
            response.set_validation_fail(message='처음으로 돌아가기 위해서는 "처음으로 돌아가기"라고 입력해주세요\n계정등록을 중간에 중지한 경우 계정이 등록되지 않습니다.\n\n')
            return response.get_response_200()

        isFloat = True
        try:
            float(value)
        except ValueError:
            isFloat = False
        if not isFloat:
            response.set_validation_fail(message='몸무게는 숫자로 입력해주세요.')
            return response.get_response_400()

        response.set_validation_success(value=value)
        return response.get_response_200()


class ValidatePatientVision(CreateAPIView):
    serializer_class = PatientCreateSerializer
    model_class = PatientCreateSerializer.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        response = ResponseBuilder(response_type=ResponseBuilder.VALIDATION)
        value = request.data['value']['origin']
        
        if value=='처음으로':
            response.set_validation_fail(message='처음으로 돌아가기 위해서는 "처음으로 돌아가기"라고 입력해주세요\n계정등록을 중간에 중지한 경우 계정이 등록되지 않습니다.\n\n')
            return response.get_response_200()
        
        isFloat = True
        try:
            float(value)
        except ValueError:
            isFloat = False
        if not isFloat:
            response.set_validation_fail(message='전화번호는 01012345678과 같은 형태로 입력해주세요.')
            return response.get_response_400()
        
        response.set_validation_success(value=value)
        return response.get_response_200()
