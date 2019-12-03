import datetime
import json

from django.http import Http404
from django.utils import timezone

from core.api.serializers import MeasurementResultSerializer
from core.api.util.helper import KakaoResponseAPI
from core.models import MeasurementResult


def get_now():
    return timezone.now().time()


def get_recent_noti_time(noti_time_list, now_time):
    s = sorted(noti_time_list)
    if len(s) == 0:
        return None
    try:
        return next(s[i - 1] for i, x in enumerate(s) if x > now_time)
    except StopIteration:
        return None


def get_recent_noti_time_num(noti_time_list, recent_noti_time):
    return [i + 1 for i, x in enumerate(noti_time_list) if x == recent_noti_time][0]


def get_recent_measurement_result(patient) -> MeasurementResult:
    noti_time_list = patient.measurement_noti_time_list()
    now_time = get_now()
    recent_noti_time = get_recent_noti_time(noti_time_list=noti_time_list, now_time=now_time)

    if recent_noti_time is None:
        return None

    if now_time > recent_noti_time:
        date = timezone.datetime.today().date()
    else:
        date = timezone.datetime.today().date() - timezone.timedelta(days=1)
    noti_time_num = get_recent_noti_time_num(noti_time_list, recent_noti_time)
    recent_measurement_result = patient.measurement_results.filter(measurement_time_num=noti_time_num, date=date)

    if recent_measurement_result.exists():
        recent_measurement_result = recent_measurement_result.get()
    else:
        data = {
            'patient': patient.id,
            'date': date,
            'medication_time_num': noti_time_num,
            'measured_at': datetime.datetime.now()
        }
        serializer = MeasurementResultSerializer(data=data)
        if serializer.is_valid():
            recent_measurement_result = serializer.save()

    return recent_measurement_result


class MeasurementResultCheck(KakaoResponseAPI):
    serializer_class = MeasurementResultSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()
        response = self.build_response(response_type=self.RESPONSE_SKILL)

        if not (
                patient.measurement_manage_flag and patient.measurement_noti_flag and patient.daily_measurement_count > 0):
            response.add_simple_text(text='산소포화도 측정 알림을 먼저 등록하셔야 해요.')
            return response.get_response_200()

        recent_measurement_result = get_recent_measurement_result(patient)

        if recent_measurement_result:
            recent_measurement_result.oxygen_saturation = self.data.get('oxygen_saturation')
            recent_measurement_result.save()
            return response.get_response_200()

        response.add_simple_text(text='알 수 없는 오류가 발생하였습니다')
        return response.get_response_200()


class MeasurementResultCheckFromNotification(KakaoResponseAPI):
    serializer_class = MeasurementResultSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        self.preprocess(request)
        try:
            patient = self.get_object_by_kakao_user_id()
        except Http404:
            return self.build_response_fallback_404()
        response = self.build_response(response_type=self.RESPONSE_SKILL)

        if not (
                patient.measurement_manage_flag and patient.measurement_noti_flag and patient.daily_measurement_count > 0):
            response.add_simple_text(text='산소포화도 측정 알림을 먼저 등록하셔야 해요.')
            return response.get_response_200()

        recent_measurement_result = get_recent_measurement_result(patient)

        if recent_measurement_result:
            try:
                param = json.loads(self.data.get('oxygen_saturation'))
            except json.JSONDecodeError:
                param = json.loads(self.data.get('oxygen_saturation').replace('\\', ''))

            oxygen_saturation = param['amount']
            recent_measurement_result.oxygen_saturation = oxygen_saturation
            recent_measurement_result.save()
            return response.get_response_200()

        response.add_simple_text(text='알 수 없는 오류가 발생하였습니다')
        return response.get_response_200()
