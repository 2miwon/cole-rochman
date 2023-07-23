from django.utils import timezone
from datetime import timedelta
import datetime
from core.models import MedicationResult

# 최근 days 일간의 정보
def get_last_info_mdResult(days: int, pid):
    tday = timezone.now()
    thirty_days_ago = tday - timedelta(days)
    return MedicationResult.objects.filter(patient__id__contains=pid, 
                                           date__range=(thirty_days_ago, tday)).order_by('-medication_time')[:days]

# 최근 days 일동안의 총 복약 횟수
def get_last_success(days, month_mdresult):
    rst = 0
    for i in range(0, days):
        if(i<len(month_mdresult)):
            if(month_mdresult[i].is_success()):
                rst += 1
    return rst

# 최근 days 일간의 부작용 보고 횟수
def get_last_sideeffect(days, month_mdresult):
    rst = 0
    for i in range(0, days):
        if(i<len(month_mdresult)):
           if(month_mdresult[i].is_side_effect()):
                rst += 1
    return rst

def get_year_month_days():
    day_list = str(datetime.datetime.now())[0:10].split('-')
    return day_list

def get_year():
    return int(get_year_month_days()[0])

def get_month():
    return int(get_year_month_days()[1])

def get_day():
    return int(get_year_month_days()[2])

def get_prev_month(m, y):
    if m == 1:
        return y - 1, 12
    else:
        return y, m - 1

def get_next_month(m, y):
    if m == 12:
        return y + 1, 1
    else:
        return y, m + 1