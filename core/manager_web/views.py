from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from core.models import Patient, MeasurementResult, MedicationResult
from datetime import timedelta
import datetime
from django.utils import timezone
from django.http import HttpResponseRedirect
from core.day import *
import calendar # 달력에서 사용합니다
from core.models.patient import Patient , Pcr_Inspection, Sputum_Inspection
from django.core import serializers



# 환자 선택 전 환자관리 대시보드
@login_required()
def user_dashboard(request):
    sort_policy = request.GET.get('sort', 'id')
    context = dict(
        patientlist=Patient.objects.filter(
            hospital__id__contains=request.user.profile.hospital.id,
            display_dashboard=True,
            treatment_end_date__gt=timezone.now(),  
        ).order_by(sort_policy),
    )
    pl = Patient.objects.filter(hospital__id__contains=request.user.profile.hospital.id)
    return render(request, "dashboard.html", context)


# 환자 선택 후 환자관리 대시보드
@login_required()
def patient_status(request, pid):
    # 보고자 하는 일주일의 월요일 날짜가 출력됨
    # 예) 2023-01-30
    d = get_date(request.GET.get("week", None))
    m = get_week(request.GET.get("month", None))

    sort = request.GET.get('sort', '-id')
    if(sort == 'id'):
        sort = '-id'
    sort_policy = sort

    # 클릭한 환자
    clickedpatient = Patient.objects.get(id=pid)
    # 결핵치료과정 퍼센트 계산
    if clickedpatient.treatment_started_date:
        if clickedpatient.treatment_end_date:
            diff1 = (
                clickedpatient.treatment_end_date
                - clickedpatient.treatment_started_date
            )
            diff2 = (
                datetime.datetime.now().date() - clickedpatient.treatment_started_date
            )
        else:
            clickedpatient.set_default_end_date()
            clickedpatient.save()
            diff1 = (
                clickedpatient.treatment_end_date
                - clickedpatient.treatment_started_date
            )
            diff2 = (
                datetime.datetime.now().date() - clickedpatient.treatment_started_date
            )

        if diff1.total_seconds() == 0:
            percent = 1
        else:
            if diff2.total_seconds() < 0:
                diff2 = diff1
            percent = diff2.total_seconds() / diff1.total_seconds()
            if percent > 1:
                percent = 1

    else:
        percent = 1

    p_str = "{0:.0%}".format(percent).rstrip("%")

    context = dict(
        p_str=p_str,
        clickedpatient=Patient.objects.filter(id=pid),
        patientlist=Patient.objects.filter(
            hospital__id__contains=request.user.profile.hospital.id,
            display_dashboard=True,
            treatment_end_date__gt=timezone.now(),  
        ).order_by(sort_policy),
        a=MeasurementResult.objects.filter(
            patient__id__contains=pid,
            measured_at__gte=cal_start_end_day(d, 1),
            measured_at__lte=cal_start_end_day(d, 7),
        ),

        prev_week=prev_week(d),
        next_week=next_week(d),

        pid=pid,
        day_list=get_weekday_list(d),
        code_hyphen=clickedpatient.code_hyphen(),
        # ! 달력에서 사용할 context들입니다. 여기서 선언만 한 뒤 아래에서 정제
        day="",
        month="",
        year="",
        # weekday="",
        today = "",
        day_of_the_week_list = "",
        calendar_day_list = []
    )

    for date in Patient.objects.filter(
        id__contains=pid,
        next_visiting_date_time__gte=cal_start_end_day(d, 1),
        next_visiting_date_time__lte=cal_start_end_day(d, 7),
    ):
        context["visiting_num"] = (
            int(date.next_visiting_date_time.isocalendar()[2] - 1) * 9.5 + 2
        )
    #        context['visiting_num'] = (int(date.next_visiting_date_time.isocalendar()[2]) - 1) * 144 + 56
    #        context['visiting_num'] = (int(date.next_visiting_date_time.isocalendar()[2]) - 1) * 144 + 140
    daily_hour_list = list()

    try:
        if clickedpatient.daily_medication_count:
            if clickedpatient.daily_medication_count >= 1:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(clickedpatient.medication_noti_time_1.hour).zfill(2),
                        str(clickedpatient.medication_noti_time_1.minute).zfill(2),
                    )
                )

            if clickedpatient.daily_medication_count >= 2:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(clickedpatient.medication_noti_time_2.hour).zfill(2),
                        str(clickedpatient.medication_noti_time_2.minute).zfill(2),
                    )
                )

            if clickedpatient.daily_medication_count >= 3:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(clickedpatient.medication_noti_time_3.hour).zfill(2),
                        str(clickedpatient.medication_noti_time_3.minute).zfill(2),
                    )
                )

            if clickedpatient.daily_medication_count >= 4:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(clickedpatient.medication_noti_time_4.hour).zfill(2),
                        str(clickedpatient.medication_noti_time_4.minute).zfill(2),
                    )
                )

            if clickedpatient.daily_medication_count >= 5:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(clickedpatient.medication_noti_time_5.hour).zfill(2),
                        str(clickedpatient.medication_noti_time_5.minute).zfill(2),
                    )
                )

    except AttributeError:
        daily_hour_list = ["재설정 필요"]

    context["daily_hour_list"] = daily_hour_list

    mdresult = [dict() for _ in range(7)]

    for i in range(1, 8):
        dailyresult = MedicationResult.objects.filter(
            patient__id__contains=pid, date=cal_start_end_day(d, i)
        )
        sideeffect = []
        succ_count = 0
        for r in dailyresult:
            if r.status == "SUCCESS":
                # mdresult[i-1][r.medication_time_num] = "복약 성공"
                succ_count += 1
            elif r.status == "DELAYED_SUCCESS":
                # mdresult[i-1][r.medication_time_num] = "성공(지연)"
                pass
            elif r.status == "NO_RESPONSE":
                # mdresult[i-1][r.medication_time_num] = "응답 없음"
                pass
            elif r.status == "FAILED":
                # mdresult[i-1][r.medication_time_num] = "복약 실패"
                pass
            elif r.status == "SIDE_EFFECT":
                symptom_more = r.symptom_name.count(",")
                succ_count += 1
                if symptom_more >= 1:
                    # mdresult[i-1][r.medication_time_num - 1] = r.symptom_name #str(r.symptom_name.split(',')[0] + " 외 " + str(symptom_more) + "개")
                    pass
                else:
                    # mdresult[i-1][r.medication_time_num - 1] = str(r.symptom_name)
                    pass
                now = r.checked_at
                symptom_names = r.symptom_name.split(",")
                symptom_severity1s = r.symptom_severity1.split(",")
                symptom_severity2s = r.symptom_severity2.split(",")
                symptom_severity3s = r.symptom_severity3.split(",")
                symptom_num = len(symptom_names)
                for j in range(symptom_num):
                    # sideeffect.append('{} => {}: {} {} {}'.format(str(now), str(symptom_names[j]), str(symptom_severity1s[j]), str(symptom_severity2s[j]), str(symptom_severity3s[j])))
                    sideeffect = symptom_names
        mdresult[i - 1]["total"] = clickedpatient.daily_medication_count
        mdresult[i - 1]["medication"] = succ_count
        mdresult[i - 1]["sideeffect"] = sideeffect
    context["mdresult"] = mdresult

    month_mdresult = get_last_info_mdResult(30, pid)
    total_mdresult = get_total_info_mdResult(pid)

    context["side_effect_static"] = get_static_sideEffect(month_mdresult)

    #count_succ = get_last_success(30, month_mdresult)
    count_succ = get_total_success(total_mdresult)
    context["count_succ"] = count_succ
    # context["per_succ"] = int(100 * count_succ / 30)
    context["per_succ"] = int(100 * count_succ / len(total_mdresult))
    context["total_medi"] = len(total_mdresult)

    count_side = get_last_sideeffect(30, month_mdresult)
    # count_side = get_total_sideeffect(total_mdresult)
    context["count_side"] = count_side
    context["per_side"] = int(100 * count_side / 30)
    # context["per_side"] = int(100 * count_side / len(total_mdresult))

    # 관리 현황 정렬    
    today_su_list = MedicationResult.objects.filter(
        patient__id__contains=pid, date=datetime.date.today(), status="SUCCESS"
    )
    today_se_list = MedicationResult.objects.filter(
        patient__id__contains=pid, date=datetime.date.today(), status="SIDE_EFFECT"
    )
    remain = 0
    if len(today_su_list):
        for mr in today_su_list:
            if mr.medication_time_num > remain:
                remain = mr.medication_time_num
    if len(today_se_list):
        for mr in today_se_list:
            if mr.medication_time_num > remain:
                remain = mr.medication_time_num
    context["remain"] = clickedpatient.daily_medication_count - remain

    # 달력 
    if(m):
        picked_year = m.year
        picked_month = m.month
        picked_day=str(datetime.date.today())[-2:]
    else:
        picked_year = str(datetime.date.today())[0:4]
        picked_month = str(datetime.date.today())[5:7]
        picked_day=str(datetime.date.today())[8:10]

    datetime_list = get_now_ymd_list()
    year = int(picked_year)
    month = int(picked_month)
    day = [int(picked_day)]
    print_year = int(picked_year)

    prev_year, prev_month = get_prev_month(month, year)
    next_year, next_month = get_next_month(month, year)

    date = datetime.datetime(year=year, month=month, day=1).date()
    day_of_month = calendar.monthrange(date.year, date.month)[1]
    day_list = []
    for i in range(1, day_of_month+1):
        day_list.append(i)

    #날짜의 시작 날짜인 1일을 무슨 요일에 시작하는지를 계산하여 달력에 표시
    day_of_the_week = datetime.date(year, month, 1).weekday() #weekday --> 날짜의 요일을 숫자로 출력
    day_of_the_week_list = []
    if day_of_the_week == 6:
        pass
    else:
        for j in range(day_of_the_week+1):
            day_of_the_week_list.append(' ')
    
    weekday = weekInt_to_str((day_of_the_week + int(picked_day) - 1) % 7)
    
    MedicationResult.objects.filter(patient__id__contains=pid)

    month_first_day = datetime.date(year, month, 1)

    week_date_list = []
    month_data_list = []
    for i in range(1,8):
        week_date_list.append(cal_start_end_day(d,i))
    for i in range(1,calendar.monthrange(d.year, d.month)[1]):
        month_data_list.append(get_date(str(month_first_day.year) + ',' + str(month_first_day.month) + ',' + str(i)))

    weekly_sputum = get_sputum_data(pid, week_date_list)
    monthly_sputum = get_sputum_data(pid, month_data_list)

    context["day"]=day
    context["month"]=month
    context["year"]=year
    # context["weekday"]=weekday
    context["today"] = day
    context["day_of_the_week_list"] = day_of_the_week_list
    context["calendar_day_list"] = day_list
    context["prev_year"]=prev_year
    context["prev_month"]=prev_month
    context["next_year"]=next_year
    context["next_month"]=next_month
    context["md_success_list"]= monthly_list(clickedpatient,year,month)[0]
    context["md_side_effect_list"]= monthly_list(clickedpatient,year,month)[1]
    context["visit_list"]=monthly_list(clickedpatient,year,month)[2]
    context["weekly_sputum"]=weekly_sputum
    context["monthly_sputum"]=monthly_sputum

    for i in context:
        print(i,context[i])
        
    return render(request, "dashboard.html", context)


# 환자 선택 전 [도말배양]
@login_required()
def inspection(request):
    sort_policy = request.GET.get('sort', 'id')
    context = dict(
        patientlist=Patient.objects.filter(
            hospital__id__contains=request.user.profile.hospital.id,
            display_dashboard=True,
        ).order_by(sort_policy),
    )
    pl = Patient.objects.filter(hospital__id__contains=request.user.profile.hospital.id)
    return render(request, "dashboard_inspection.html", context)

# 환자 선택 후 [도말배양]
@login_required()
def patient_inspection(request, pid):

    # 클릭한 환자
    clickedpatient = Patient.objects.get(id=pid)

    sort_policy = request.GET.get('sort', 'id')

    daily_hour_list = list()


    try:
        if clickedpatient.daily_medication_count:
            if clickedpatient.daily_medication_count >= 1:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(clickedpatient.medication_noti_time_1.hour).zfill(2),
                        str(clickedpatient.medication_noti_time_1.minute).zfill(2),
                    )
                )

            if clickedpatient.daily_medication_count >= 2:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(clickedpatient.medication_noti_time_2.hour).zfill(2),
                        str(clickedpatient.medication_noti_time_2.minute).zfill(2),
                    )
                )

            if clickedpatient.daily_medication_count >= 3:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(clickedpatient.medication_noti_time_3.hour).zfill(2),
                        str(clickedpatient.medication_noti_time_3.minute).zfill(2),
                    )
                )

            if clickedpatient.daily_medication_count >= 4:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(clickedpatient.medication_noti_time_4.hour).zfill(2),
                        str(clickedpatient.medication_noti_time_4.minute).zfill(2),
                    )
                )

            if clickedpatient.daily_medication_count >= 5:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(clickedpatient.medication_noti_time_5.hour).zfill(2),
                        str(clickedpatient.medication_noti_time_5.minute).zfill(2),
                    )
                )

    except AttributeError:
        daily_hour_list = ["재설정 필요"]
    
    context = dict(
        clickedpatient=Patient.objects.filter(id=pid),
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
        code_hyphen=clickedpatient.code_hyphen(),
        daily_hour_list=daily_hour_list,
        sputum=Sputum_Inspection.objects.filter(patient_set=pid)
    )

    return render(request, "dashboard_inspection.html", context)

# 도말배양 - 검사결과 업데이트 모달
@login_required()
def patient_inspection_update(request, pid, sputum_id):

    # 클릭한 환자
    clickedpatient = Patient.objects.get(id=pid)

    # 클릭한 검사결과 id
    clickedSputum = Sputum_Inspection.objects.get(id=sputum_id)


    daily_hour_list = list()


    try:
        if clickedpatient.daily_medication_count:
            if clickedpatient.daily_medication_count >= 1:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(clickedpatient.medication_noti_time_1.hour).zfill(2),
                        str(clickedpatient.medication_noti_time_1.minute).zfill(2),
                    )
                )

            if clickedpatient.daily_medication_count >= 2:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(clickedpatient.medication_noti_time_2.hour).zfill(2),
                        str(clickedpatient.medication_noti_time_2.minute).zfill(2),
                    )
                )

            if clickedpatient.daily_medication_count >= 3:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(clickedpatient.medication_noti_time_3.hour).zfill(2),
                        str(clickedpatient.medication_noti_time_3.minute).zfill(2),
                    )
                )

            if clickedpatient.daily_medication_count >= 4:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(clickedpatient.medication_noti_time_4.hour).zfill(2),
                        str(clickedpatient.medication_noti_time_4.minute).zfill(2),
                    )
                )

            if clickedpatient.daily_medication_count >= 5:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(clickedpatient.medication_noti_time_5.hour).zfill(2),
                        str(clickedpatient.medication_noti_time_5.minute).zfill(2),
                    )
                )

    except AttributeError:
        daily_hour_list = ["재설정 필요"]
    
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
        daily_hour_list=daily_hour_list,
        sputum=Sputum_Inspection.objects.filter(id=pid),
        clicked_sputum = clickedSputum
    )

    return render(request, "dashboard_inspection_update.html", context)


def sign_in(request):
    msg = []
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("web_menu")

        else:
            msg.append("아이디 또는 비밀번호 오류입니다.")
    else:
        msg.append("")

    return render(request, "login.html", {"errors": msg})


@login_required()
def web_menu(request):
    return render(request, "web_menu.html")


def get_date(req_day):
    if req_day:
        req_tuple = req_day.split(",")
        return datetime.date(int(req_tuple[0]), int(req_tuple[1]), int(req_tuple[2]))
    return datetime.datetime.now()

def get_week(req_mon):
    if req_mon:
        req_tuple = req_mon.split(",")
        return datetime.date(int(req_tuple[0]), int(req_tuple[1]), 1)
    return datetime.datetime.now()

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
    #datetime_list = get_now_ymd_list()
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
        dailyresult=MedicationResult.objects.filter(patient__code__contains=patient.code, date=date_str)
        med_cnt = 0

        if patient.next_visiting_date_time:
            if patient.next_visiting_date_time.date() == date_str:
                visit_list.append(int(i))

        for r in dailyresult:
            #복약 상태별 날짜의 일수들을 각각 상태 리스트에 분류하여 넣는다
            if r.status == "SUCCESS":
                med_cnt += 1
                if patient.daily_medication_count == med_cnt:
                    md_success_list.append(int(i))
            elif r.status=='DELAYED_SUCCESS':
                md_delayed_success_list.append(int(i))
            elif r.status=='NO_RESPONSE':
                md_no_response_list.append(int(i))
            elif r.status=='FAILED':
                md_failed_list.append(int(i))
            elif r.status=='SIDE_EFFECT':
                med_cnt += 1
                md_side_effect_list.append(int(i))
                if patient.daily_medication_count == med_cnt:
                    md_success_list.append(int(i))
    return md_success_list, md_side_effect_list, visit_list

def get_date_str(date: datetime.date, day: int):
    return get_date(str(date.year) + ',' + str(date.month) + ',' + str(day))

# 도말배양
def get_sputum_data(patient_id, date):
    return serializers.serialize("json", Sputum_Inspection.objects.filter(patient_set=patient_id, insp_date__in=date))

def get_monthly_dayList_int(date):
    day_of_month = calendar.monthrange(date.year, date.month)[1]
    day_list = []
    for i in range(1, day_of_month+1):
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
    if(count):
        for i in rst:
            rst[i] = int(100 * rst[i] / count)
    return rst
    

# @login_required()
# def symptom(request, pid, sid):
#    clickedpatient = Patient.objects.get(id=pid)
