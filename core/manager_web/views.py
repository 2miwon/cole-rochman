from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from core.models import Patient, MeasurementResult, MedicationResult
import datetime


# 환자 선택 전 환자관리 대시보드
@login_required()
def user_dashboard(request):
    context = dict(
        patientlist=Patient.objects.filter(hospital__id__contains=request.user.profile.hospital.id),

    )
    pl = Patient.objects.filter(hospital__id__contains=request.user.profile.hospital.id)
    return render(request, 'dashboard.html', context)


# 환자 선택 후 환자관리 대시보드
@login_required()
def patient_status(request, pid):
    # 보고자 하는 일주일의 월요일 날짜가 출력됨
    # 예) 2023-01-30
    d = get_date(request.GET.get('week', None))

    # 클릭한 환자
    clickedpatient = Patient.objects.get(id=pid)
    # 결핵치료과정 퍼센트 계산
    if clickedpatient.treatment_started_date:
        if clickedpatient.treatment_end_date:
            diff1 = clickedpatient.treatment_end_date - clickedpatient.treatment_started_date
            diff2 = datetime.datetime.now().date() - clickedpatient.treatment_started_date
        else:
            clickedpatient.set_default_end_date()
            clickedpatient.save()
            diff1 = clickedpatient.treatment_end_date - clickedpatient.treatment_started_date
            diff2 = datetime.datetime.now().date() - clickedpatient.treatment_started_date

        if diff1.total_seconds() == 0:
            percent=1
        else:
            if diff2.total_seconds() < 0:
                diff2 = diff1
            percent = diff2.total_seconds() / diff1.total_seconds()
            if percent > 1:
                percent = 1

    else:
        percent=1

    p_str = "{0:.0%}".format(percent).rstrip('%')

    context = dict(
        p_str=p_str,
        clickedpatient=Patient.objects.filter(id=pid),
        patientlist=Patient.objects.filter(hospital__id__contains=request.user.profile.hospital.id),
        a=MeasurementResult.objects.filter(patient__id__contains=pid, measured_at__gte=cal_start_end_day(d, 1),
                                           measured_at__lte=cal_start_end_day(d, 7)),
        prev_week=prev_week(d),
        next_week=next_week(d),
        pid=pid,
        day_list=print_day_list(d),
    )

    
    for date in Patient.objects.filter(id__contains=pid, next_visiting_date_time__gte=cal_start_end_day(d, 1),
                                       next_visiting_date_time__lte=cal_start_end_day(d, 7)):
        context['visiting_num'] = int(date.next_visiting_date_time.isocalendar()[2] - 1) * 9.5 + 2
#        context['visiting_num'] = (int(date.next_visiting_date_time.isocalendar()[2]) - 1) * 144 + 56
#        context['visiting_num'] = (int(date.next_visiting_date_time.isocalendar()[2]) - 1) * 144 + 140
    daily_hour_list = list()

    try:
        if (clickedpatient.daily_medication_count):
            if (clickedpatient.daily_medication_count >= 1):

                daily_hour_list.append('{}:{}'.format(str(clickedpatient.medication_noti_time_1.hour).zfill(2), str(clickedpatient.medication_noti_time_1.minute).zfill(2)))


            if (clickedpatient.daily_medication_count >= 2):
                daily_hour_list.append('{}:{}'.format(str(clickedpatient.medication_noti_time_2.hour).zfill(2),
                                                      str(clickedpatient.medication_noti_time_2.minute).zfill(2)))

            if (clickedpatient.daily_medication_count >= 3):
                daily_hour_list.append('{}:{}'.format(str(clickedpatient.medication_noti_time_3.hour).zfill(2),
                                                      str(clickedpatient.medication_noti_time_3.minute).zfill(2)))

            if (clickedpatient.daily_medication_count >= 4):
                daily_hour_list.append('{}:{}'.format(str(clickedpatient.medication_noti_time_4.hour).zfill(2),
                                                      str(clickedpatient.medication_noti_time_4.minute).zfill(2)))


            if (clickedpatient.daily_medication_count >= 5):
                daily_hour_list.append('{}:{}'.format(str(clickedpatient.medication_noti_time_5.hour).zfill(2),
                                                      str(clickedpatient.medication_noti_time_5.minute).zfill(2)))

    except AttributeError:
        daily_hour_list=['재설정 필요']

    context["daily_hour_list"] = daily_hour_list

    mdresult = [ [ "" for _ in range(clickedpatient.daily_medication_count) ] for _ in range(7)]

    #for i in range(clickedpatient.daily_medication_count):
    #    mdresult.append(["O","O","","","O","",""])
    #    mdresult.append(["","","","","","O",""])
    #    mdresult.append(["","","","","","O",""])
    #    mdresult.append(["","","","","","",""])
#    mdresult=[["","","","","","",""],["","","","","","",""],["","","","","","",""],["","","","","","",""],["","","","","","",""]]
    sideeffect=[]
    mediresult = MedicationResult.objects.filter(patient__id__contains=pid, date__gte=cal_start_end_day(d, 1),
                                        date__lte=cal_start_end_day(d, 7))

    for i in range(1,8):
#        dailyresult=MedicationResult.objects.filter(patient__id__contains=pid, date=d + datetime.timedelta(days = i - 1))
#        print(dailyresult)
        dailyresult=MedicationResult.objects.filter(patient__id__contains=pid, date=cal_start_end_day(d, i))
        for r in dailyresult:
            if r.status=="SUCCESS":
                mdresult[i-1][r.medication_time_num - 1] = "복약 성공"
            elif r.status=='DELAYED_SUCCESS':
                mdresult[i-1][r.medication_time_num - 1] = "성공(지연)"
            elif r.status=='NO_RESPONSE':
                mdresult[i-1][r.medication_time_num - 1] = "응답 없음"
            elif r.status=='FAILED':
                mdresult[i-1][r.medication_time_num - 1] = "복약 실패"
            elif r.status=='SIDE_EFFECT':
                symptom_more = r.symptom_name.count(",")
                if symptom_more >= 1:
                    mdresult[i - 1][r.medication_time_num - 1] = str(r.symptom_name.split(',')[0] + " 외 " + str(symptom_more) + "개")
                else:
                    mdresult[i - 1][r.medication_time_num - 1] = str(r.symptom_name)
                now = r.checked_at
                symptom_names = r.symptom_name.split(',')
                symptom_severity1s = r.symptom_severity1.split(',')
                symptom_severity2s = r.symptom_severity2.split(',')
                symptom_severity3s = r.symptom_severity3.split(',')
                symptom_num = len(symptom_names)
                for i in range(symptom_num):
                    sideeffect.append('{} => {}: {} {} {}'.format(str(now), str(symptom_names[i]), str(symptom_severity1s[i]), str(symptom_severity2s[i]), str(symptom_severity3s[i])))     

    context['mdresult']=mdresult
    context['sideeffect']=sideeffect

    today_su_list = MedicationResult.objects.filter(patient__id__contains=pid, date=datetime.date.today(), status = 'SUCCESS')
    today_se_list = MedicationResult.objects.filter(patient__id__contains=pid, date=datetime.date.today(), status = 'SIDE_EFFECT')
    remain = 0
    print(today_su_list)
    if len(today_su_list):
        for mr in today_su_list:
            if mr.medication_time_num > remain:
                remain = mr.medication_time_num
    if len(today_se_list):
        for mr in today_se_list:
            if mr.medication_time_num > remain:
                remain = mr.medication_time_num
    print(" remain = ", remain)
    context['remain']= clickedpatient.daily_medication_count - remain

    return render(request, 'dashboard.html', context)


def sign_in(request):
    msg = []
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('web_menu')

        else:
            msg.append('아이디 또는 비밀번호 오류입니다.')
    else:
        msg.append('')

    return render(request, 'login.html', {'errors': msg})


@login_required()
def web_menu(request):
    return render(request, 'web_menu.html')


def get_date(req_day):
    if req_day:
        req_tuple = req_day.split(',')
        return datetime.date(int(req_tuple[0]), int(req_tuple[1]), int(req_tuple[2]))
    return datetime.datetime.now()


def prev_week(d):
    pre_day = d - datetime.timedelta(days=7)
    return 'week=' + str(pre_day.year) + ',' + str(pre_day.month) + ',' + str(pre_day.day)


def next_week(d):
    pre_day = d + datetime.timedelta(days=7)
    return 'week=' + str(pre_day.year) + ',' + str(pre_day.month) + ',' + str(pre_day.day)


def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = datetime.date(iso_year, 1, 4)
    delta = datetime.timedelta(fourth_jan.isoweekday() - 1)
    return fourth_jan - delta


def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + datetime.timedelta(days=iso_day - 1, weeks=iso_week - 1)


def cal_start_end_day(dt, i):
    iso = dt.isocalendar()
    iso = list(iso)
    iso[2] = i
    iso = tuple(iso)
    return iso_to_gregorian(*iso)


def print_day_list(dt):
    iso = dt.isocalendar()
    li = list()
    for i in range(1, 8):
        iso = list(iso)
        iso[2] = i
        iso = tuple(iso)
        yo = ''
        if (i == 1):
            yo = '월'
        elif (i == 2):
            yo = '화'
        elif (i == 3):
            yo = '수'
        elif (i == 4):
            yo = '목'
        elif (i == 5):
            yo = '금'
        elif (i == 6):
            yo = '토'
        elif (i == 7):
            yo = '일'
        li.append(str(iso_to_gregorian(*iso).month).zfill(2) + '.' + str(iso_to_gregorian(*iso).day).zfill(2) + ' ' + yo)
    return li
    
    # 추가
#@login_required()
#def symptom(request, pid, sid):
#    clickedpatient = Patient.objects.get(id=pid)

