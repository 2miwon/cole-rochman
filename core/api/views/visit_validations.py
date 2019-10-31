import re

from rest_framework import status
from rest_framework.response import Response

from core.api.util.helper import KakaoResponseAPI


class ValidateTimeBefore(KakaoResponseAPI):
    def post(self, request, format='json', *args, **kwargs):
        SECONDS_FOR_MINUTE = 60
        SECONDS_FOR_HOUR = 60 * SECONDS_FOR_MINUTE
        SECONDS_FOR_DAY = 24 * SECONDS_FOR_HOUR

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
            response_data = {
                "status": "FAIL"
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            "status": "SUCCESS",
            "value": timedelta
        }
        return Response(response_data, status=status.HTTP_200_OK)
