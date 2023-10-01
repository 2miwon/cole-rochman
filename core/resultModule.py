from django.utils import timezone
from core.models import MedicationResult
from datetime import timedelta

def get_total_info_mdResult(pid: int):
    """
    총 복약 관련 정보
    pid : 해당 환자 id
    output : MedicationResult 객체 리스트
    """
    return MedicationResult.objects.filter(patient__id__contains=pid).order_by('-medication_time')

def get_last_info_mdResult(days: int, pid: int):
    """
    최근 days 일간의 정보
    days : 오늘 기준 검색을 원하는 날짜 범위
    pid : 환자 id
    output : MedicationResult 객체 리스트
    """
    tday = timezone.now()
    thirty_days_ago = tday - timedelta(days)
    return MedicationResult.objects.filter(patient__id__contains=pid, 
                                           date__range=(thirty_days_ago, tday)).order_by('-medication_time')[:days]

def get_total_success(pid: int):
    """
    전체 복약 성공 횟수
    pid : 해당 환자 id
    output : MedicationResult 객체 리스트
    """
    mdresult = get_total_info_mdResult(pid)
    rst = 0
    for i in range(0, len(mdresult)):
        if(mdresult[i].is_success()):
            rst += 1
    return rst

def get_success_count(mdresult_list) -> int:
    """
    해당 복약 기록들 중 총 복약 성공 횟수
    mdresult_list : 해당하는 복약 기록 리스트
    output : 총 복약 성공 횟수
    """
    rst = 0
    days = len(mdresult_list)
    for i in range(0, days):
        if(mdresult_list[i].is_success()):
            rst += 1
    return rst

def get_last_success(days: int, mdresult_list):
    """
    최근 days 일동안의 총 복약 성공 횟수
    days : 오늘 기준 검색을 원하는 날짜 범위
    mdresult_list : 해당하는 복약 기록 리스트
    output : 총 복약 성공 횟수
    """
    rst = 0
    for i in range(0, days):
        if(i<len(mdresult_list)):
            if(mdresult_list[i].is_success()):
                rst += 1
    return rst

def get_total_sideeffect(pid: int) -> int:
    """
    전체 부작용 보고 횟수
    pid : 해당 환자 id
    output : 부작용 보고 횟수
    """
    mdresult = get_total_info_mdResult(pid)
    rst = 0
    for i in range(0, len(mdresult)):
        if(mdresult[i].is_side_effect()):
            rst += 1
    return rst

# 해당 복약 기록들 중 총 부작용 보고 횟수
    

def get_last_sideeffect(days, mdresult_list):
    """
    최근 days 일간의 부작용 보고 횟수
    days : 오늘 기준 검색을 원하는 날짜 범위
    pid : 해당 환자 id
    output : 부작용 보고 횟수
    """
    rst = 0
    for i in range(0, days):
        if(i<len(mdresult_list)):
           if(mdresult_list[i].is_side_effect()):
                rst += 1
    return rst