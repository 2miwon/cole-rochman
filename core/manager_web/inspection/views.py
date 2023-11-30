from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from core.models import Patient, MeasurementResult, MedicationResult
from core.models.patient import Patient, Pcr_Inspection, Sputum_Inspection
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponseRedirect
from core.utils.dayModule import *
import calendar
from django.core import serializers
import datetime
from .forms import InspectionForm
from django.core.paginator import Paginator


# 환자 선택 전 [도말배양]
@login_required()
def inspection(request):
    sort_policy = request.GET.get("sort", "-id")
    context = dict(
        patientlist=Patient.objects.filter(
            hospital__id__contains=request.user.profile.hospital.id,
            display_dashboard=True,
        ).order_by(sort_policy),
    )
    return render(request, "dashboard_inspection.html", context)


# 환자 선택 후 [도말배양]
@login_required()
def patient_inspection(request, pid):
    if request.method == "POST":
        form = InspectionForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.patient_set = Patient.objects.get(id=pid)
            data.save()
        else:
            print(form.errors)
    if request.method == "DELETE":
        print(request.DELETE)
        Sputum_Inspection.objects.filter(id=request.POST.get("sputum_id")).delete()

    today = datetime.date.today().strftime("%Y-%m-%d")

    start_date = request.GET.get("start_date", None)
    end_date = request.GET.get("end_date", today)
    page = request.GET.get("page", 1)
    # 기본 정렬 기준
    sort_policy = request.GET.get("sort", "-id")

    clickedpatient = Patient.objects.filter(id=pid)

    if start_date and end_date:
        sputum = Sputum_Inspection.objects.filter(
            patient_set=pid, insp_date__gte=start_date, insp_date__lte=end_date
        ).order_by("-id")
    else:
        sputum = Sputum_Inspection.objects.filter(patient_set=pid).order_by("-id")
    sputum_pagination = list(range(len(sputum) // 10 + 1))

    paginator = Paginator(sputum, 10)
    page_obj = paginator.get_page(page)

    context = dict(
        clickedpatient=clickedpatient,
        patientlist=Patient.objects.filter(
            hospital__id__contains=request.user.profile.hospital.id,
            display_dashboard=True,
        ).order_by(sort_policy),
        a=MeasurementResult.objects.filter(
            patient__id__contains=pid,
            # measured_at__gte=cal_start_end_day(d, 1),
            # measured_at__lte=cal_start_end_day(d, 7),
        ),
        pid=pid,
        daily_hour_list=get_daily_noti_time_list(clickedpatient),
        sputum=page_obj,
        sputum_pagination=sputum_pagination,
        today=today,
        range_ten=list(range(10)),
    )

    return render(request, "dashboard_inspection.html", context)


# def patient_inspection_create(request, pid):
#     return patient_inspection(request, pid)


# 도말배양 - 검사결과 업데이트 모달
@login_required()
def patient_inspection_update(request, pid, sputum_id):
    if request.method == "POST":
        form = InspectionForm(request.POST)
        if form.is_valid():
            Sputum_Inspection.objects.filter(id=sputum_id).update(
                insp_date=request.POST.get("insp_date"),
                method=request.POST.get("method"),
                th=request.POST.get("th"),
                smear_result=request.POST.get("smear_result"),
                culture_result=request.POST.get("culture_result"),
            )
        else:
            print(form.errors)
        redirect("patient_inspection", pid=pid)
        return HttpResponseRedirect(request.path_info)

    # 기본 정렬 기준
    sort_policy = request.GET.get("sort", "-id")

    # 클릭한 환자
    clickedpatient = Patient.objects.get(id=pid)

    # 클릭한 검사결과 id
    clickedSputum = Sputum_Inspection.objects.get(id=sputum_id)

    formatted_insp_date = clickedSputum.insp_date.strftime("%Y-%m-%d")
    today = datetime.date.today().strftime("%Y-%m-%d")

    context = dict(
        clickedpatient=Patient.objects.filter(id=pid),
        patientlist=Patient.objects.filter(
            hospital__id__contains=request.user.profile.hospital.id,
            display_dashboard=True,
        ),
        a=MeasurementResult.objects.filter(
            patient__id__contains=pid,
            # measured_at__gte=cal_start_end_day(d, 1),
            # measured_at__lte=cal_start_end_day(d, 7),
        ),
        pid=pid,
        code_hyphen=clickedpatient.code_hyphen(),
        daily_hour_list=get_daily_noti_time_list(clickedpatient),
        sputum=Sputum_Inspection.objects.filter(id=pid),
        clicked_sputum=clickedSputum,
        formatted_insp_date=formatted_insp_date,
        today=today,
    )

    return render(request, "dashboard_inspection_update.html", context)


def cal_start_end_day(dt, i):
    iso = dt.isocalendar()
    iso = list(iso)
    iso[2] = i
    iso = tuple(iso)
    return iso_to_gregorian(*iso)


def get_month_data(dt):
    pass

    # 추가


def get_query_string():
    pass


# 나중에 정리할게요 코드 그대로 갖다썼는데 진짜 말도안되는 코드...
def monthly_list(patient, year, month):
    # datetime_list = get_now_ymd_list()
    date = datetime.datetime(year, month, day=1).date()
    print(date)
    visit_list = []
    md_success_list = []
    md_delayed_success_list = []
    md_no_response_list = []
    md_failed_list = []
    md_side_effect_list = []

    for i in get_monthly_dayList_int(date):
        date_str = get_date_str(date, i)
        dailyresult = MedicationResult.objects.filter(
            patient__code__contains=patient.code, date=date_str
        )
        med_cnt = 0

        if patient.next_visiting_date_time:
            if patient.next_visiting_date_time.date() == date_str:
                visit_list.append(int(i))

        for r in dailyresult:
            # 복약 상태별 날짜의 일수들을 각각 상태 리스트에 분류하여 넣는다
            if r.status == "SUCCESS":
                med_cnt += 1
                if patient.daily_medication_count == med_cnt:
                    md_success_list.append(int(i))
            elif r.status == "DELAYED_SUCCESS":
                md_delayed_success_list.append(int(i))
            elif r.status == "NO_RESPONSE":
                md_no_response_list.append(int(i))
            elif r.status == "FAILED":
                md_failed_list.append(int(i))
            elif r.status == "SIDE_EFFECT":
                med_cnt += 1
                md_side_effect_list.append(int(i))
                if patient.daily_medication_count == med_cnt:
                    md_success_list.append(int(i))
    return md_success_list, md_side_effect_list, visit_list


def get_date_str(date: datetime.date, day: int):
    return get_date(str(date.year) + "," + str(date.month) + "," + str(day))


# 도말배양
def get_sputum_data(pid: int, date):
    return serializers.serialize(
        "json", Sputum_Inspection.objects.filter(patient_set=pid, insp_date__in=date)
    )


def get_monthly_dayList_int(date):
    day_of_month = calendar.monthrange(date.year, date.month)[1]
    day_list = []
    for i in range(1, day_of_month + 1):
        day_list.append(i)
    return day_list


def get_static_sideEffect(results: MedicationResult):
    rst = {
        "식욕 감소": 0,
        "메스꺼움": 0,
        "구토": 0,
        "속 쓰림": 0,
        "무른 변/설사": 0,
        "피부 발진": 0,
        "가려움증": 0,
        "시야장애": 0,
        "관절통": 0,
        "피로": 0,
        "기타": 0,
    }
    count = 0
    for i in results:
        if i.is_side_effect():
            for j in i.get_sideEffect_type():
                rst[j] += 1
                count += 1
    if count:
        for i in rst:
            rst[i] = int(100 * rst[i] / count)
    return rst


def get_daily_noti_time_list(patient: Patient):
    rst = list()
    try:
        for i in range(0, patient.daily_medication_count):
            rst.append(time_formatiing(patient.get_noti_time_by_num))
        return rst
    except AttributeError:
        return ["재설정 필요"]


def set_default_context(request):
    if len(request.GET) == 0:
        pass
    sort_policy = request.GET.get("sort", "-id")
    if sort_policy == "id":
        sort_policy = "-id"
    rst = dict(
        patientlist=Patient.objects.filter(
            hospital__id__contains=request.user.profile.hospital.id,
            display_dashboard=True,
            treatment_end_date__gt=timezone.now(),
        ).order_by(sort_policy),
    )
    return rst


# @login_required()
# def symptom(request, pid, sid):
#    clickedpatient = Patient.objects.get(id=pid)
