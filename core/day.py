from django.utils import timezone
from datetime import timedelta
import datetime
from core.models import MedicationResult
from enum import Enum

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

def get_now_ymd_list():
    day_list = str(datetime.datetime.now())[0:10].split('-')
    return day_list

def get_year():
    return int(get_now_ymd_list()[0])

def get_month():
    return int(get_now_ymd_list()[1])

def get_day():
    return int(get_now_ymd_list()[2])

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
    
# offset -1 이면 이전달, 2이면 다다음달
def navigate_month(m, y, offset):
    y += (m + offset - 1) // 12
    m = (m + offset - 1) % 12 + 1
    return y, m
    
def prev_week(d: datetime.datetime):
    pre_day = d - datetime.timedelta(days=7)
    return 'week=' + str(pre_day.year) + ',' + str(pre_day.month) + ',' + str(pre_day.day)

def next_week(d: datetime.datetime):
    pre_day = d + datetime.timedelta(days=7)
    return 'week=' + str(pre_day.year) + ',' + str(pre_day.month) + ',' + str(pre_day.day)

def get_weekday_list(dt: datetime.datetime):
    iso = dt.isocalendar()
    li = list()
    for i in range(0, 7):
        iso = list(iso)
        iso[2] = i+1
        iso = tuple(iso)
        yo = weekInt_to_str(i)
        li.append(
            str(iso_to_gregorian(*iso).month).zfill(2)
            + "."
            + str(iso_to_gregorian(*iso).day).zfill(2)
            + " "
            + yo
        )
    return li

def weekInt_to_str(weekday: int):
    if weekday == 0:
        return '월'
    elif weekday == 1:
        return '화'
    elif weekday == 2:
        return '수'
    elif weekday == 3:
        return '목'
    elif weekday == 4:
        return '금'
    elif weekday == 5:
        return '토'
    elif weekday == 6:
        return '일'
    else:
        return 'error'

def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = datetime.date(iso_year, 1, 4)
    delta = datetime.timedelta(fourth_jan.isoweekday() - 1)
    return fourth_jan - delta

def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + datetime.timedelta(days=iso_day - 1, weeks=iso_week - 1)

class Weekday(Enum):
    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6

    def __str__(self):
        return self.name
    
