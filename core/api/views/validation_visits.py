import re

from core.api.serializers import PatientCreateSerializer
from core.api.util.helper import KakaoResponseAPI


class ValidateTimeBefore(KakaoResponseAPI):
    serializer_class = PatientCreateSerializer
    model_class = serializer_class.Meta.model
    queryset = model_class.objects.all()

    def post(self, request, format='json', *args, **kwargs):
        SECONDS_FOR_MINUTE = 60
        SECONDS_FOR_HOUR = 60 * SECONDS_FOR_MINUTE
        SECONDS_FOR_DAY = 24 * SECONDS_FOR_HOUR

        response = self.build_response(response_type=self.RESPONSE_VALIDATION)

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
            response.set_validation_fail()
            return response.get_response_400()

        response.set_validation_success(value=timedelta)
        return response.get_response_200()
