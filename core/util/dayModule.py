from django.utils import timezone
from datetime import timedelta
import datetime
from enum import Enum
from calendar import monthrange

MINUTES = 60
HOURS = 60 * MINUTES
DAYS = 24 * HOURS

def get_date(req_day) -> datetime:
    """
    req_day : "yyyy,mm,dd"
    output : date(년,월,일)
    default : today
    """
    if req_day:
        req_tuple = req_day.split(",")
        return datetime.date(int(req_tuple[0]), int(req_tuple[1]), int(req_tuple[2]))
    return datetime.datetime.now()


def get_month_first_date(req_day) -> datetime:
    """
    req_day : "yyyy,mm,dd"
    output : date(년,월, 1일)
    default : today
    """
    if req_day:
        req_tuple = req_day.split(",")
        return datetime.date(int(req_tuple[0]), int(req_tuple[1]), 1)
    return datetime.datetime.now()


def get_today() -> datetime:
    """
    output : datetime (오늘 날짜를 "yyyy-mm-dd" 형식으로 반환)
    """
    return datetime.date.today().strftime("%Y-%m-%d")


def get_date_text_kor(date: datetime.date, short_year: bool) -> str:
    """
    date : 해당 날짜
    short_year : True일 시 년도를 yy로 표시 (20yy)
    output: "yyyy년 mm월 dd일"
    default : today
    """
    y_indicator = "%Y"
    if short_year:
        y_indicator = "%y"
    if date:
        return date.strftime(y_indicator + "년 %m월 %d일")
    return datetime.date.today().strftime("%Y년 %m월 %d일")


def get_date_text_simple(date: datetime.date, short_year: bool) -> str:
    """
    date : 해당 날짜
    short_year : True일 시 년도를 yy로 표시 (20yy)
    output : "yyyy.mm.dd"
    default : today
    """
    y_indicator = "%Y"
    if short_year:
        y_indicator = "%y"
    if date:
        return date.strftime(y_indicator + ".%m.%d")
    return datetime.date.today().strftime(y_indicator + ".%m.%d")


# hh:mm
def time_formatiing(time) -> str:
    return "{}:{}".format(str(time.hour).zfill(2), str(time.minute).zfill(2))


def week_first_day(date):
    pass


def week_last_day(date):
    pass


def month_first_day(date):
    return datetime.date(date.year, date.month, 1)


def month_last_day(date):
    return datetime.date(date.year, date.month, monthrange(date.year, date.month)[1])


# 누적
# def count(length: int, condition) -> int:
#     rst = 0
#     for i in range(0, length):
#         if(condition):
#             rst += 1
#     return rst


def get_now_time():
    return datetime.datetime.now().time()


def get_now_date():
    pass


def get_now_ymd_list() -> list[str]:
    day_list = str(datetime.datetime.now())[0:10].split("-")
    return day_list


def get_now_year() -> int:
    return int(get_now_ymd_list()[0])


def get_now_month() -> int:
    return int(get_now_ymd_list()[1])


def get_now_day() -> int:
    return int(get_now_ymd_list()[2])


#
# 이전, 다음 Month, Week 관련 함수
#
def get_prev_month(m: int, y: int):
    if m == 1:
        return y - 1, 12
    else:
        return y, m - 1


def get_next_month(m: int, y: int):
    if m == 12:
        return y + 1, 1
    else:
        return y, m + 1


def navigate_month(m: int, y: int, offset: int):
    """
    offset -1 이면 이전달, 2이면 다다음달
    output : (year, month)
    """
    y += (m + offset - 1) // 12
    m = (m + offset - 1) % 12 + 1
    return y, m


def prev_week(d: datetime.datetime):
    pre_day = d - datetime.timedelta(days=7)
    return (
        "week=" + str(pre_day.year) + "," + str(pre_day.month) + "," + str(pre_day.day)
    )


def next_week(d: datetime.datetime):
    pre_day = d + datetime.timedelta(days=7)
    return (
        "week=" + str(pre_day.year) + "," + str(pre_day.month) + "," + str(pre_day.day)
    )


def navigete_week(d: datetime.datetime, offset: int) -> datetime.datetime:
    """
    offset -1 이면 이전주, 2이면 다다음주
    output : datetime.datetime
    """
    return d + datetime.timedelta(days=7 * offset)


def get_weekday_list(dt: datetime.datetime):
    """
    dt : 해당 날짜
    output : 해당 날짜의 주의 요일 리스트 [09.25 월, 09.26 화, ...]
    """
    iso = dt.isocalendar()
    li = list()
    for i in range(0, 7):
        iso = list(iso)
        iso[2] = i + 1
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
        return "월"
    elif weekday == 1:
        return "화"
    elif weekday == 2:
        return "수"
    elif weekday == 3:
        return "목"
    elif weekday == 4:
        return "금"
    elif weekday == 5:
        return "토"
    elif weekday == 6:
        return "일"
    else:
        return "error"


def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = datetime.date(iso_year, 1, 4)
    delta = datetime.timedelta(fourth_jan.isoweekday() - 1)
    return fourth_jan - delta


def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + datetime.timedelta(days=iso_day - 1, weeks=iso_week - 1)


def get_date_by_weekday(date: datetime.date, weekday: int):
    """
    date : 해당 날짜
    weekday : 1=monday ~ 7=sunday
    output : 해당 날짜의 주의 weekday번째 날짜
    """
    iso = list(date.isocalendar())
    iso[2] = weekday  #
    return iso_to_gregorian(*iso)


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
