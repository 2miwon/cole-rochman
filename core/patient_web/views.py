import code
from contextlib import nullcontext
import email
import imp
from multiprocessing import context
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.models.certification import Certificaion
from core.models.measurement_result import MeasurementResult
from core.models.medication_result import MedicationResult
from core.models.patient import Patient
from django.contrib.auth.models import User
from django.contrib import auth
import datetime
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

def sign_up(request):
    msg = []
    if request.method == "POST":
        username = request.POST['username']
        patient = Patient.objects.all().filter(code = username)
        user = User.objects.all().filter(username=username)
        if user:
            msg.append('이미 존재하는 회원입니다!')
            return render(request,'signup.html',{'errors': msg})
        if patient:
            if request.POST['password1']==request.POST['password2']:
                user=User.objects.create_user(request.POST['username'], password=request.POST['password1'], email=request.POST['email'])
                auth.login(request,user,backend='django.contrib.auth.backends.ModelBackend')
                patient.user = request.user
                return redirect('login_patient')
            else:
                msg.append('비밀번호와 비밀번호 재입력 칸이 서로 다릅니다!')
        else:
            msg.append('해당 환자코드가 존재하지 않습니다!')

    else:
        msg.append('')
            
            #아이디 값을 환자코드로 입력하세요 라는 오류 메시지
    return render(request,'signup.html',{'errors': msg})

def sign_in(request):
    msg = []
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('patient_main_page')
        else:
            msg.append('존재하는 아이디가 없거나 비밀번호가 일치 안합니다')
    else:
        msg.append('')

    return render(request, 'patient_login.html', {'errors': msg})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            
        else:
            messages.error(request, 'Please correct the error below.')
        return redirect('login_patient')
    else:
        form = PasswordChangeForm(request.user)
        return render(request, 'patient_change_password.html', {
        'form': form
        })

@login_required
def main(request):
    return render(request, 'patient_main_page.html')

@login_required
def patient_dahboard(request):
    patient = Patient.objects.get(code = request.user.username)

    #치료 과정 코드
    if patient.treatment_started_date:
        if patient.treatment_end_date:
            total_cure_period = patient.treatment_end_date - patient.treatment_started_date
            current_cure_period = datetime.datetime.now().date() - patient.treatment_started_date
        else:
            patient.set_default_end_date()
            patient.save()
            total_cure_period = patient.treatment_end_date - patient.treatment_started_date
            current_cure_period = datetime.datetime.now().date() - patient.treatment_started_date
        
        if total_cure_period.total_seconds() == 0:
            percent = 1
        else:
            if current_cure_period.total_seconds() < 0:
                current_cure_period = total_cure_period
            percent = current_cure_period.total_seconds() / total_cure_period.total_seconds()
            if percent > 1:
                percent = 1
    else:
        percent = 1
    
    p_str = "{0:.0%}".format(percent).rstrip('%')

    #다음 내원 예정일
    d = get_date(request.GET.get('week', None))
    visiting_num=0
    for date in Patient.objects.filter(code__contains=request.user.username, next_visiting_date_time__gte=cal_start_end_day(d, 1), next_visiting_date_time__lte=cal_start_end_day(d, 7)):
        visiting_num = (int(date.next_visiting_date_time.isocalendar()[2]) - 1) * 144 + 140
    
    #daily_hour_list
    daily_hour_list = list()

    try:
        if (patient.daily_medication_count):
            if (patient.daily_medication_count >= 1):

                daily_hour_list.append('{}:{}'.format(str(patient.medication_noti_time_1.hour).zfill(2), str(patient.medication_noti_time_1.minute).zfill(2)))


            if (patient.daily_medication_count >= 2):
                daily_hour_list.append('{}:{}'.format(str(patient.medication_noti_time_2.hour).zfill(2),
                                                      str(patient.medication_noti_time_2.minute).zfill(2)))

            if (patient.daily_medication_count >= 3):
                daily_hour_list.append('{}:{}'.format(str(patient.medication_noti_time_3.hour).zfill(2),
                                                      str(patient.medication_noti_time_3.minute).zfill(2)))

            if (patient.daily_medication_count >= 4):
                daily_hour_list.append('{}:{}'.format(str(patient.medication_noti_time_4.hour).zfill(2),
                                                      str(patient.medication_noti_time_4.minute).zfill(2)))


            if (patient.daily_medication_count >= 5):
                daily_hour_list.append('{}:{}'.format(str(patient.medication_noti_time_5.hour).zfill(2),
                                                      str(patient.medication_noti_time_5.minute).zfill(2)))


    except AttributeError:
        daily_hour_list=['재설정 필요']

    #복약 성공 여부
    mdresult=[["","","","","","",""],["","","","","","",""],["","","","","","",""],["","","","","","",""],["","","","","","",""]]
    for i in range(1,8):
        dailyresult=MedicationResult.objects.filter(patient__code__contains=request.user.username, date=cal_start_end_day(d, i))
        for r in dailyresult:
            #medication_time_num == 1:
            if r.status=="SUCCESS":
                mdresult[r.medication_time_num-1][i-1]="복약 성공"
            elif r.status=='DELAYED_SUCCESS':
                mdresult[r.medication_time_num - 1][i - 1] = "성공(지연)"
            elif r.status=='NO_RESPONSE':
                mdresult[r.medication_time_num - 1][i - 1] = "응답 없음"
            elif r.status=='FAILED':
                mdresult[r.medication_time_num - 1][i - 1] = "복약 실패"
            elif r.status=='SIDE_EFFECT':
                mdresult[r.medication_time_num - 1][i - 1] = "부작용"
    
    #산소 포화도
    msresult = [0, 0, 0, 0, 0, 0, 0]
    msresult2 = ['None', 'None', 'None', 'None', 'None', 'None', 'None']
    dailycount = 0
    for i in range(1, 8):
        dailymearesult = MeasurementResult.objects.filter(patient__code__contains=request.user.username,
                                                          measured_at__gte=cal_start_end_day(d, i),date__lte=cal_start_end_day(d, 7))
        for r in dailymearesult:
            msresult[i - 1] += r.oxygen_saturation
            print(r.oxygen_saturation)
            dailycount += 1
        if msresult[i - 1] == 0 or dailycount == 0:
            msresult[i - 1] = 'None'
        else:
            msresult[i - 1] = int(msresult[i - 1] / dailycount)
            if msresult[i-1]<=80 and msresult[i-1]>0:
                msresult2[i - 1] = msresult[i - 1]
                msresult[i-1]='None'

        dailycount=0
    res_msresult= msresult
    res_msresult2=msresult2
    msresult = [0, 0, 0, 0, 0, 0, 0]
    msresult2 = ['None', 'None', 'None', 'None', 'None', 'None', 'None']
    

    context = {
        'treat_started_date':patient.treatment_started_date,
        'treat_end_date':patient.treatment_end_date,
        'cure_progress' : p_str,
        'patient' : patient,
        'day_list':print_day_list(d),
        "daily_hour_list":daily_hour_list,
        'visiting_num': visiting_num,
        'prev_week':prev_week(d),
        'next_week':next_week(d),
        'mdresult': mdresult,
        'msresult':res_msresult,
        'msresult2':res_msresult2

    }
    return render(request, 'patient_dashboard.html', context=context)


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
def get_date(req_day):
    if req_day:
        req_tuple = req_day.split(',')
        return datetime.date(int(req_tuple[0]), int(req_tuple[1]), int(req_tuple[2]))
    return datetime.datetime.now()

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

def prev_week(d):
    pre_day = d - datetime.timedelta(days=7)
    return 'week=' + str(pre_day.year) + ',' + str(pre_day.month) + ',' + str(pre_day.day)


def next_week(d):
    pre_day = d + datetime.timedelta(days=7)
    return 'week=' + str(pre_day.year) + ',' + str(pre_day.month) + ',' + str(pre_day.day)

def certification_number():
    number = ''
    for i in range(4):
        a = random.randint(1,9)
        number+= str(a)
    return int(number)

def temporary_password():
    random_password_char = [[0,1,2,3,4,5,6,7,8,9], ['a','b','k','d','e','f','z','y','x','e']]
    temporary_password = ''
    for i in range(12):
        a = random.randint(0,1)
        b = random.randint(0,9)
        temporary_password += str(random_password_char[a][b])
    return temporary_password

def password_reset(request):
    msg = []
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        certificate_number = str(certification_number())
        if 'certification' in request.POST:
            for i in User.objects.filter(username = username):
                if i.email == email:
                    sender = settings.EMAIL_SENDER
                    reciever = i.email
                    message = Mail( from_email=sender,
                                    to_emails=reciever,
                                    subject='cole-rochman 인증번호입니다',
                                    html_content='<strong>' +certificate_number + '</strong>')
                    try:
                        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                        response = sg.send(message)
                        print(response.status_code)
                        print(response.body)
                        print(response.headers)
                        certification = Certificaion.objects.get(user__username = username)
                        print(certification)
                        if certification:
                            certification.number = int(certificate_number)
                            certification.save()
                        else:
                            certification = Certificaion(user = i, number = int(certificate_number))
                            certification.save()
                        msg.append('인증번호가 발송되었습니다!')
                    except Exception as e:
                        print(e.message)
                    print("success")
            context = {'username':username, 'email':email, 'msg':msg}
            return render(request,'password_reset.html',context)
        elif 'submit' in request.POST:
            certification = Certificaion.objects.get(user__username=username)
            print("인증번호: ",certification.number)
            print(request.POST['user_certificate_number'])
            if certification.number == int(request.POST['user_certificate_number']):
                certification.number = int(certification_number())
                certification.save()
                user = User.objects.get(username = username)
                password = temporary_password()
                user.set_password(password)
                user.save()
                sender = settings.EMAIL_SENDER
                reciever = user.email
                message = Mail( from_email=sender,
                                to_emails=reciever,
                                subject='cole-rochman 임시 비밀번호입니다',
                                html_content='<strong>' +password + '</strong>')
                try:
                    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                    response = sg.send(message)
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                except Exception as e:
                    print(e.message)
                print("success")
                return render(request, "password_reset_success.html")
            else:
                msg.append('인증번호가 다릅니다!')
                return render(request, 'password_reset.html', {'errors':msg})
    else:
        msg.append('')
        return render(request, 'password_reset.html')

