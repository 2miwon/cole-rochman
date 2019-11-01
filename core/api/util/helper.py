import functools

from rest_framework.generics import GenericAPIView, get_object_or_404

from core.api.util.response_builder import ResponseBuilder
from core.models import Patient


# decorators
def require_kakao_user_id(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.kakao_user_id_parsed:
            self.parse_kakao_user_id()
        return method(self, *args, **kwargs)

    return wrapper


def require_patient_code(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.patient_code_parsed:
            self.parse_patient_code()
        return method(self, *args, **kwargs)

    return wrapper


def find_nested_key_from_dict(_dict: dict, keys):
    """
    :param _dict: dictionary to parse. e.g. request.data
    :param keys: string with delimiter. e.g. 'action.detailParams'
    :return: dict or str
    """
    try:
        for key in keys.split('.'):
            _dict = _dict.get(key)
        return _dict
    except AttributeError:
        return None


class Kakao:
    """
    :var data: saving dict data from request_data parsed
    """
    DATETIME_FORMAT_STRING = '%Y-%m-%dT%H:%M:%S'

    RESPONSE_VALIDATION = 'validation'
    RESPONSE_SKILL = 'skill'

    def __init__(self):
        self.request_data = {}

        self.kakao_user_id = ''
        self.patient_code = ''
        self.params = {}
        self.detail_params = {}

        self.data = {}
        self.params_parsed = False
        self.detail_params_parsed = False
        self.kakao_user_id_parsed = False
        self.patient_code_parsed = False

    def preprocess(self, request):
        self.request_data = request.data
        self.parse_detail_params()
        # detailParams보다 정확한 params의 데이터 확보를 위해 순서 는 params를 마지막으로
        self.parse_params()

    def __parse_request(self, keys):
        result = find_nested_key_from_dict(self.request_data, keys)
        return result

    def parse_params(self):
        keys = 'action.params'
        parsed = self.__parse_request(keys)
        if parsed is None:
            return
        setattr(self, 'params', parsed)
        self.params_parsed = True
        self.data.update(parsed)

    def parse_detail_params(self):
        keys = 'action.detailParams'
        parsed = self.__parse_request(keys)
        if parsed is None:
            return
        for key, value in parsed.items():
            self.detail_params[key] = value['value']

        self.detail_params_parsed = True
        self.data.update(self.detail_params)

    def parse_kakao_user_id(self):
        parsed = self.__parse_request(keys='userRequest.user.id')  # TODO parse 할수없는 경우 400 response -> 모든 폴백에 적용 고려
        setattr(self, 'kakao_user_id', parsed)
        self.kakao_user_id_parsed = True
        self.data.update({'kakao_user_id': parsed})

    def parse_patient_code(self):
        code = self.params.get('patient_code')
        code = code or self.detail_params.get('patient_code')

        self.data.update({'code': code})
        self.patient_code = code
        self.patient_code_parsed = True

    @staticmethod
    def build_response(response_type):
        return ResponseBuilder(response_type)


class KakaoResponseAPI(Kakao, GenericAPIView):
    serializer_class = None
    queryset = None
    lookup_field = 'kakao_user_id'
    response = {}

    @require_kakao_user_id
    def get_object_by_kakao_user_id(self) -> Patient:
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {self.lookup_field: self.kakao_user_id}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
