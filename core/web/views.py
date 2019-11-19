from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from core.models import Patient, MeasurementResult, MedicationResult
import datetime


@login_required()
def user_dashboard(request):
    context = dict(
        patientlist=Patient.objects.filter(hospital__id__contains=request.user.profile.hospital.id),

    )
    pl = Patient.objects.filter(hospital__id__contains=request.user.profile.hospital.id)
    print(pl)

    return render(request, 'dashboard.html', context)


@login_required()
def patient_status(request, pid):
    d = get_date(request.GET.get('week', None))

    clickedpatient = Patient.objects.get(id=pid)
    diff1 = clickedpatient.treatment_end_date - clickedpatient.treatment_started_date
    diff2 = datetime.datetime.now().date() - clickedpatient.treatment_started_date
    if (diff2.total_seconds() < 0):
        diff2 = diff1
    if diff1.total_seconds() == 0:
        percent = 1
    else:
        percent = diff2.total_seconds() / diff1.total_seconds()

    p_str = "{0:.0%}".format(percent).rstrip('%')

    context = dict(
        p_str=p_str,
        clickedpatient=Patient.objects.filter(id=pid),
        patientlist=Patient.objects.filter(hospital__id__contains=request.user.profile.hospital.id),
        a=MeasurementResult.objects.filter(patient__id__contains=pid, measured_at__gte=cal_start_end_day(d, 1),
                                           measured_at__lte=cal_start_end_day(d, 7)),
        b=MedicationResult.objects.filter(patient__id__contains=pid, date__gte=cal_start_end_day(d, 1),
                                          date__lte=cal_start_end_day(d, 7)),
        prev_week=prev_week(d),
        next_week=next_week(d),
        pid=pid,
        day_list=print_day_list(d),

    )
    for date in Patient.objects.filter(id__contains=pid, next_visiting_date_time__gte=cal_start_end_day(d, 1),
                                       next_visiting_date_time__lte=cal_start_end_day(d, 7)):
        context['visiting_num'] = (int(date.next_visiting_date_time.isocalendar()[2]) - 1) * 144 + 140
    daily_hour_list = list()
    if (clickedpatient.daily_medication_count >= 1):
        daily_hour_list.append(
            str(clickedpatient.medication_noti_time_1.hour) + ":" + str(clickedpatient.medication_noti_time_1.minute))
    if (clickedpatient.daily_medication_count >= 2):
        daily_hour_list.append(
            str(clickedpatient.medication_noti_time_2.hour) + ":" + str(clickedpatient.medication_noti_time_2.minute))
    if (clickedpatient.daily_medication_count >= 3):
        daily_hour_list.append(
            str(clickedpatient.medication_noti_time_3.hour) + ":" + str(clickedpatient.medication_noti_time_3.minute))
    if (clickedpatient.daily_medication_count >= 4):
        daily_hour_list.append(
            str(clickedpatient.medication_noti_time_4.hour) + ":" + str(clickedpatient.medication_noti_time_4.minute))
    if (clickedpatient.daily_medication_count >= 5):
        daily_hour_list.append(
            str(clickedpatient.medication_noti_time_5.hour) + ":" + str(clickedpatient.medication_noti_time_5.minute))
    context["daily_hour_list"] = daily_hour_list

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
            msg.append('존재하는 아이디가 없거나 비밀번호가 일치 안합니다')
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
        li.append(str(iso_to_gregorian(*iso).month) + ' / ' + str(iso_to_gregorian(*iso).day) + ' ' + yo)
    return li
