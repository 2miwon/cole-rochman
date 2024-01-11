import calendar
import code
from contextlib import nullcontext
import email
from http.client import REQUEST_ENTITY_TOO_LARGE
import imp
from multiprocessing import context
from unicodedata import category
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.models import profile
from core.models.measurement_result import MeasurementResult
from core.models.medication_result import MedicationResult
from core.models.patient import Patient, Pcr_Inspection, Sputum_Inspection
from core.models.community import Post, Comment
from core.models.profile import Profile
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import os
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
import random
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from core.models.certification import Certificaion
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from django.http import HttpResponseRedirect
from core.util.dayModule import *
from core.util.resultModule import *

load_dotenv()

def sign_up(request):
    msg = []
    if request.method == "POST":
        username = request.POST["username"]
        patient = Patient.objects.all().filter(code=username)
        user = User.objects.all().filter(username=username)
        if user:
            msg.append("이미 존재하는 회원입니다!")
            return render(request, "signup.html", {"errors": msg})
        if patient:
            if request.POST["password1"] == request.POST["password2"]:
                user = User.objects.create_user(
                    request.POST["username"],
                    password=request.POST["password1"],
                    email=request.POST["email"],
                )
                profile = Profile()
                profile.user = user
                profile.nickname = request.POST["nickname"]
                profile.save()
                auth.login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                patient.user = request.user
                return redirect("login_patient")
            else:
                msg.append("비밀번호와 비밀번호 재입력 칸이 서로 다릅니다!")
        else:
            msg.append("해당 환자코드가 존재하지 않습니다!")

    else:
        msg.append("")

        # 아이디 값을 환자코드로 입력하세요 라는 오류 메시지
    return render(request, "signup.html", {"errors": msg})


def sign_in(request):
    try:
        if request.user.is_superuser:
            return redirect("/manager/menu")
        patient = Patient.objects.get(code=request.user.username)
        if patient:
            return redirect("patient_dashboard")
    except:
        pass
    msg = []
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return redirect("/manager/menu")
            else:
                return redirect("patient_dashboard")
        else:
            msg.append("존재하는 아이디가 없거나 비밀번호가 일치하지 않습니다!")
    else:
        msg.append("")

    return render(request, "patient_login.html", {"errors": msg})


@login_required(login_url="/", redirect_field_name="next")
def change_password(request):
    form = PasswordChangeForm(request.user)
    if request.method == "POST":
        user = form.save()
        messages.success(request, "비밀번호가 성공적으로 변경되었습니다!")
        return redirect("login_patient")
    else:
        return render(request, "patient_change_password.html", {"form": form})


#    if request.method == 'POST':
#        form = PasswordChangeForm(request.user, request.POST)
#        user = form.save()
#        update_session_auth_hash(request, user)  # Important!
#        messages.success(request, '비밀번호가 성공적으로 변경되었습니다!')
#
#
#        return redirect('login_patient')
#
#    else:
#        form = PasswordChangeForm(request.user)
#    return render(request, 'patient_change_password.html', {'form': form})


@login_required
def main(request):
    return render(request, "patient_main_page.html")


# 특정일을 클릭하기 전 달력 대시보드
@login_required(login_url="/", redirect_field_name="next")
def patient_dashboard(request):
    patient = Patient.objects.get(code=request.user.username)
    pid = patient.id
    nickname = patient.nickname

    start_date = ""
    end_date = ""

    # 치료 시작일, 종료 예정일 출력, 치료 과정 코드
    if patient.treatment_started_date:
        start_date = "{}.{}.{}".format(
            str(patient.treatment_started_date.year)[2:4],
            str(patient.treatment_started_date.month).zfill(2),
            str(patient.treatment_started_date.day).zfill(2),
        )
        if patient.treatment_end_date:
            total_cure_period = (
                patient.treatment_end_date - patient.treatment_started_date
            )
            current_cure_period = (
                datetime.datetime.now().date() - patient.treatment_started_date
            )
        else:
            patient.set_default_end_date()
            patient.save()
            total_cure_period = (
                patient.treatment_end_date - patient.treatment_started_date
            )
            current_cure_period = (
                datetime.datetime.now().date() - patient.treatment_started_date
            )
        end_date = "{}.{}.{}".format(
            str(patient.treatment_end_date.year)[2:4],
            str(patient.treatment_end_date.month).zfill(2),
            str(patient.treatment_end_date.day).zfill(2),
        )

        if total_cure_period.total_seconds() == 0:
            percent = 1
        else:
            if current_cure_period.total_seconds() < 0:
                current_cure_period = total_cure_period
            percent = (
                current_cure_period.total_seconds() / total_cure_period.total_seconds()
            )
            if percent > 1:
                percent = 1
    else:
        percent = 1

    p_str = "{0:.0%}".format(percent).rstrip("%")

    # 복약 성공률
    med_tot = len(MedicationResult.objects.filter(patient__code=request.user.username))
    med_cnt = len(
        MedicationResult.objects.filter(
            patient__code=request.user.username, status="PENDING"
        )
    )
    med_per = 1 - (med_cnt / med_tot)
    med_str = "{0:.0%}".format(med_per).rstrip("%")

    # 다음 내원 예정일
    d = get_date(request.GET.get("week", None))
    visiting_num = 0
    for date in Patient.objects.filter(
        code__contains=request.user.username,
        next_visiting_date_time__gte=cal_start_end_day(d, 1),
        next_visiting_date_time__lte=cal_start_end_day(d, 7),
    ):
        visiting_num = (
            int(date.next_visiting_date_time.isocalendar()[2]) - 1
        ) * 144 + 140

    # daily_hour_list
    daily_hour_list = list()

    try:
        if patient.daily_medication_count:
            if patient.daily_medication_count >= 1:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(patient.medication_noti_time_1.hour).zfill(2),
                        str(patient.medication_noti_time_1.minute).zfill(2),
                    )
                )

            if patient.daily_medication_count >= 2:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(patient.medication_noti_time_2.hour).zfill(2),
                        str(patient.medication_noti_time_2.minute).zfill(2),
                    )
                )

            if patient.daily_medication_count >= 3:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(patient.medication_noti_time_3.hour).zfill(2),
                        str(patient.medication_noti_time_3.minute).zfill(2),
                    )
                )

            if patient.daily_medication_count >= 4:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(patient.medication_noti_time_4.hour).zfill(2),
                        str(patient.medication_noti_time_4.minute).zfill(2),
                    )
                )

            if patient.daily_medication_count >= 5:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(patient.medication_noti_time_5.hour).zfill(2),
                        str(patient.medication_noti_time_5.minute).zfill(2),
                    )
                )

    except AttributeError:
        daily_hour_list = ["재설정 필요"]

    # 달력
    datetime_list = get_now_ymd_list()
    year = int(datetime_list[0])
    month = int(datetime_list[1])
    day = [int(datetime_list[2])]
    weekday = weekInt_to_str(datetime.datetime.now().weekday())

    print_year = int(datetime_list[0][2:4])

    date = datetime.datetime(
        year=int(datetime_list[0]), month=int(datetime_list[1]), day=1
    ).date()
    day_of_month = calendar.monthrange(date.year, date.month)[1]
    day_list = []
    for i in range(1, day_of_month + 1):
        day_list.append(i)
    day_of_the_week = datetime.date(year, month, 1).weekday()
    day_of_the_week_list = []
    if day_of_the_week == 6:
        pass
    else:
        for j in range(day_of_the_week + 1):
            day_of_the_week_list.append(" ")

    # 내원 여부
    visit_list = []

    # 복약 성공 여부
    md_success_list = []
    md_delayed_success_list = []
    md_no_response_list = []
    md_failed_list = []
    md_side_effect_list = []

    for i in day_list:
        date_str = ""
        date_str += str(year)
        date_str += ","
        date_str += str(month)
        date_str += ","
        i = str(i)
        date_str += i
        date_str = get_date(date_str)
        dailyresult = MedicationResult.objects.filter(
            patient__code__contains=request.user.username, date=date_str
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

    # 오늘의 복약 정리
    dailyresult = MedicationResult.objects.filter(
        patient__code__contains=request.user.username, date=str(datetime.date.today())
    )
    today_md_success_list = []
    symptom_time_list = []
    symptom_name_list = []
    symptom_sev_list1 = []
    symptom_sev_list2 = []
    symptom_sev_list3 = []
    symptoms = []

    success_cnt = 1
    sideeffect_cnt = 1
    for i in dailyresult:
        if i.status == "SUCCESS":
            if int(str(i.medication_time).split(":")[0]) == 12:
                med_time = (
                    "오후 "
                    + str(i.medication_time).split(":")[0]
                    + ":"
                    + str(i.medication_time).split(":")[1]
                )
            elif int(str(i.medication_time).split(":")[0]) >= 12:
                med_time = (
                    "오후 "
                    + str(int(str(i.medication_time).split(":")[0]) - 12)
                    + ":"
                    + str(i.medication_time).split(":")[1]
                )
            else:
                med_time = (
                    "오전 "
                    + str(i.medication_time).split(":")[0]
                    + ":"
                    + str(i.medication_time).split(":")[1]
                )

            text = str(success_cnt) + " : " + str(med_time)
            today_md_success_list.append(str(text))
            success_cnt += 1

        if i.status == "SIDE_EFFECT":
            if int(str(i.medication_time).split(":")[0]) == 12:
                med_time = (
                    "오후 "
                    + str(i.medication_time).split(":")[0]
                    + ":"
                    + str(i.medication_time).split(":")[1]
                )
            elif int(str(i.medication_time).split(":")[0]) >= 12:
                med_time = (
                    "오후 "
                    + str(int(str(i.medication_time).split(":")[0]) - 12)
                    + ":"
                    + str(i.medication_time).split(":")[1]
                )
            else:
                med_time = (
                    "오전 "
                    + str(i.medication_time).split(":")[0]
                    + ":"
                    + str(i.medication_time).split(":")[1]
                )

            text = str(success_cnt) + " : " + str(med_time)
            today_md_success_list.append(str(text))
            success_cnt += 1

            # 부작용 출력 부분 #
            symptom_names = i.symptom_name.split(",")
            question1 = "얼마나 자주"
            question2 = "가장 심할 때"
            question3 = "일상에 지장"
            symptom_severity1s = i.symptom_severity1.split(",")
            symptom_severity2s = i.symptom_severity2.split(",")
            symptom_severity3s = i.symptom_severity3.split(",")
            symptom_num = len(symptom_names)
            for i in range(symptom_num):
                symptom_name_list.append(
                    "{} : {}".format(str(sideeffect_cnt), str(symptom_names[i]))
                )
                sideeffect_cnt += 1
                symptom_time_list.append("{}".format(str(med_time)))

                symptom_sev_list1.append(
                    "{}: {}".format(str(question1), str(symptom_severity1s[i]))
                )
                symptom_sev_list2.append(
                    "{}: {}".format(str(question2), str(symptom_severity2s[i]))
                )
                symptom_sev_list3.append(
                    "{}: {}".format(str(question3), str(symptom_severity3s[i]))
                )
                symptoms = zip(
                    symptom_name_list,
                    symptom_time_list,
                    symptom_sev_list1,
                    symptom_sev_list2,
                    symptom_sev_list3,
                )

    prev_year, prev_month = get_prev_month(month, year)
    next_year, next_month = get_next_month(month, year)

    today_med_list = MedicationResult.objects.filter(
        patient__id__contains=pid, date=datetime.date.today(), status__in=["SUCCESS", "SIDE_EFFECT"]
    )

    context = {
        "nickname": nickname,
        "start_date": start_date,
        "end_date": end_date,
        "treat_started_date": patient.treatment_started_date,
        "treat_end_date": patient.treatment_end_date,
        "cure_progress": p_str,
        "med_progress": med_str,
        "patient": patient,
        "day_list": print_day_list(d),
        "daily_hour_list": daily_hour_list,
        "visiting_num": visiting_num,
        "prev_week": prev_week(d),
        "next_week": next_week(d),
        "prev_year": prev_year,
        "prev_month": int(prev_month),
        "next_month": int(next_month),
        "next_year": next_year,
        "year": year,
        "month": month,
        "day": day[0],
        "weekday": weekday,
        "print_year": print_year,
        "today": day,
        "day_list": day_list,
        "day_of_the_week_list": day_of_the_week_list,
        "visit_list": visit_list,
        "md_success_list": md_success_list,
        "md_delayed_success_list": md_delayed_success_list,
        "md_no_response_list": md_no_response_list,
        "md_failed_list": md_failed_list,
        "md_side_effect_list": md_side_effect_list,
        "today_md_success_list": today_md_success_list,
        "symptoms": symptoms,
        "daily_med_fullfill": len(today_med_list) == patient.daily_medication_count,
    }
    
    debug_context(context)

    return render(request, "patient_dashboard2.html", context=context)


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
    #'2002,2,22' 입력시 2002-02-22 의 형식으로 출력해주는 함수
    if req_day:
        req_tuple = req_day.split(",")
        return datetime.date(int(req_tuple[0]), int(req_tuple[1]), int(req_tuple[2]))
    return datetime.datetime.now()


def print_day_list(dt):
    iso = dt.isocalendar()
    li = list()
    for i in range(1, 8):
        iso = list(iso)
        iso[2] = i
        iso = tuple(iso)
        yo = ""
        if i == 1:
            yo = "월"
        elif i == 2:
            yo = "화"
        elif i == 3:
            yo = "수"
        elif i == 4:
            yo = "목"
        elif i == 5:
            yo = "금"
        elif i == 6:
            yo = "토"
        elif i == 7:
            yo = "일"
        li.append(
            str(iso_to_gregorian(*iso).month)
            + " / "
            + str(iso_to_gregorian(*iso).day)
            + " "
            + yo
        )
    return li


def certification_number():
    number = ""
    for i in range(4):
        a = random.randint(1, 9)
        number += str(a)
    return int(number)


def temporary_password():
    random_password_char = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        ["a", "b", "k", "d", "e", "f", "z", "y", "x", "e"],
    ]
    temporary_password = ""
    for i in range(12):
        a = random.randint(0, 1)
        b = random.randint(0, 9)
        temporary_password += str(random_password_char[a][b])
    return temporary_password


def password_reset(request):
    msg = []
    if request.method == "POST":
        print("request status", request.POST)
        if "modify" not in request.POST:
            username = request.POST["username"]
            email = request.POST["email"]
            certificate_number = str(certification_number())
        if "certification" in request.POST:
            print("hello certification")
            print(User.objects.all().filter(username=username))
            for i in User.objects.all().filter(username=username):
                if i.email == email:
                    try:
                        print("Certification Number:", certificate_number)
                        contents = MIMEText(
                            "<h1>[결핵챗봇 콜로그만] 인증번호입니다 </h1><hr> <br><br><h2> 안녕하세요 "
                            + username
                            + "님! <br> 결핵챗봇 콜로크만 비밀 번호 찾기를 위한<br> 인증번호입니다!</h2> <br><h2>고객님의 인증번호: <strong>"
                            + certificate_number
                            + "<strong></h2>",
                            "html",
                        )
                        message = MIMEMultipart()
                        message["Subject"] = "cole-rochman 인증번호입니다."  # 제목
                        message["From"] = os.environ.get("EMAIL_SENDER")  # 보내는이
                        message["To"] = i.email  # 받는이
                        message.attach(contents)
                        mailSend(message)
                        try:
                            certification = Certificaion.objects.get(
                                user__username=username
                            )
                            print("certifiaction exist")
                        except:
                            certification = Certificaion()
                            certification.user = i
                            certification.number = int(certificate_number)
                            certification.save()

                        if certification:
                            print("if certification")
                            certification.number = int(certificate_number)
                            certification.save()
                        else:
                            print("certification not exist")
                            certification = Certificaion(
                                user=i, number=int(certificate_number)
                            )
                            certification.save()
                        msg.append("인증번호가 발송되었습니다!")
                    except Exception as e:
                        print(e)

                    print("success")
                else:
                    msg.append("등록된 이메일과 다릅니다!")
            context = {"username": username, "email": email, "msg": msg}
            return render(request, "password_reset.html", context)
        elif "user_certificate_number" in request.POST:
            certification = Certificaion.objects.get(user__username=username)
            if certification.number == int(request.POST["user_certificate_number"]):
                """certification.number = int(certification_number())
                certification.save()
                user = User.objects.get(username = username)
                # Random PW
                password = temporary_password()
                user.set_password(password)
                user.save()

                contents = MIMEText('<h1>[결핵챗봇 콜로크만] 임시비밀번호입니다 </h1><hr> <br><br><h2> 안녕하세요 '
                                    + username+ '님! <br> 결핵챗봇 콜로크만 환자용 대쉬보드를 위한<br> 비밀번호를 안내해 드립니다.</h2> <br><h2>고객님의 임시비밀번호: <strong>'
                                    + password + '<strong></h2>', 'html')
                message = MIMEMultipart()
                message['Subject'] = 'cole-rochman 임시 비밀번호입니다' # 제목
                message['From'] = os.environ.get('EMAIL_SENDER') # 보내는이
                message['To'] = user.email # 받는이
                message.attach(contents)
                mailSend(message)

                print("success")
                """
                context = {
                    "username": username,
                }
                return render(request, "password_reset_success.html", context)

            else:
                msg.append("인증번호가 다릅니다!")
                return render(request, "password_reset.html", {"errors": msg})
        elif "modify" in request.POST:
            password = request.POST["password"]
            username = request.POST["username"]
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            return HttpResponseRedirect("/")
    else:
        msg.append("")
        return render(request, "password_reset.html")


def password_modify(request):
    username = request.POST["username"]
    if "modify" in request.POST:
        print("MODI")
        password = request.POST["PW"]
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
    else:
        return render(request, "password_reset_success.html")


def post_list(request):
    posts = Post.objects.order_by("-created_at")
    for post in posts:
        post.print_created_at = "{}.{}.{}".format(
            str(post.created_at.year)[2:4],
            str(post.created_at.month).zfill(2),
            str(post.created_at.day).zfill(2),
        )
        post.count_of_the_comment = Comment.objects.filter(post=post).count()
        post.save()
    context = {"posts": posts}
    return render(request, "community.html", context)


def post(request):
    if request.method == "POST":
        post = Post()
        print(request.POST["category"])
        post.category = request.POST["category"]
        post.anonymous = request.POST.get("anonymous", False)
        post.writer = request.user
        post.title = request.POST["title"]
        post.content = request.POST["content"]
        try:
            post.images = request.FILES["images"]
            print("이미지 업로드 성공")
        except:
            print("이미지 업로드 실패")
            pass

        post.save()
        return redirect("community_main")
    else:
        return render(request, "create.html")


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    comments = Comment.objects.filter(post=post_id)
    cnt = 0
    for comment in comments:
        comment.print_created_at = "{}.{}.{}".format(
            str(comment.created_at_comment.year)[2:4],
            str(comment.created_at_comment.month).zfill(2),
            str(comment.created_at_comment.day).zfill(2),
        )
        comment.save()
        cnt += 1

    context = {
        "post": post,
        "post_id": post_id,
        "comments": comments,
        "comment_cnt": cnt,
    }
    return render(request, "detail.html", context)


def post_delete(request, post_id):
    post = Post.objects.get(id=post_id)
    if post.writer == request.user:
        post.delete()
    return redirect("community_main")


def comment(request, post_id):
    comments = Comment.objects.filter(post=post_id)
    cnt = 0
    for comment in comments:
        comment.print_created_at = "{}.{}.{}".format(
            str(comment.created_at_comment.year)[2:4],
            str(comment.created_at_comment.month).zfill(2),
            str(comment.created_at_comment.day).zfill(2),
        )
        comment.save()
        cnt += 1
    context = {"post_id": post_id, "comments": comments, "cnt": cnt}
    return render(request, "comment.html", context)


def comment_post(request, post_id):
    comment = Comment()
    comment.writer = request.user
    comment.post = Post.objects.get(id=post_id)
    comment.comment = request.POST["comment"]
    comment.save()
    return redirect("post_detail", post_id)


def comment_delete(request, post_id, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if comment.writer == request.user:
        comment.delete()
    return redirect("post_detail", post_id)


def search(request):
    search_content = request.GET.get("search_content")
    if len(search_content) >= 1:
        search_list = Post.objects.filter(
            Q(title__contains=search_content) | Q(content__contains=search_content)
        )

    else:
        search_list = Post.objects.all()

    return render(request, "community.html", {"posts": search_list})


# 날짜별 patient_dashboard
@login_required
def patient_dashboard_by_day(
    request,
    picked_year,
    picked_month=str(datetime.date.today())[-5:-3],
    picked_day=str(datetime.date.today())[-2:],
):
    patient = Patient.objects.get(code=request.user.username)
    pid = patient.id
    nickname = patient.nickname

    start_date = ""
    end_date = ""

    # 치료 시작일, 종료 예정일 출력, 치료 과정 코드
    if patient.treatment_started_date:
        start_date = "{}.{}.{}".format(
            str(patient.treatment_started_date.year)[2:4],
            str(patient.treatment_started_date.month).zfill(2),
            str(patient.treatment_started_date.day).zfill(2),
        )
        if patient.treatment_end_date:
            total_cure_period = (
                patient.treatment_end_date - patient.treatment_started_date
            )
            current_cure_period = (
                datetime.datetime.now().date() - patient.treatment_started_date
            )
        else:
            patient.set_default_end_date()
            patient.save()
            total_cure_period = (
                patient.treatment_end_date - patient.treatment_started_date
            )
            current_cure_period = (
                datetime.datetime.now().date() - patient.treatment_started_date
            )
        end_date = "{}.{}.{}".format(
            str(patient.treatment_end_date.year)[2:4],
            str(patient.treatment_end_date.month).zfill(2),
            str(patient.treatment_end_date.day).zfill(2),
        )

        if total_cure_period.total_seconds() == 0:
            percent = 1
        else:
            if current_cure_period.total_seconds() < 0:
                current_cure_period = total_cure_period
            percent = (
                current_cure_period.total_seconds() / total_cure_period.total_seconds()
            )
            if percent > 1:
                percent = 1
    else:
        percent = 1

    p_str = "{0:.0%}".format(percent).rstrip("%")

    # 복약 성공률
    med_tot = len(MedicationResult.objects.filter(patient__code=request.user.username))
    med_cnt = len(
        MedicationResult.objects.filter(
            patient__code=request.user.username, status="PENDING"
        )
    )
    med_per = 1 - (med_cnt / med_tot)
    med_str = "{0:.0%}".format(med_per).rstrip("%")

    # 다음 내원 예정일
    d = get_date(request.GET.get("week", None))
    visiting_num = 0
    for date in Patient.objects.filter(
        code__contains=request.user.username,
        next_visiting_date_time__gte=cal_start_end_day(d, 1),
        next_visiting_date_time__lte=cal_start_end_day(d, 7),
    ):
        visiting_num = (
            int(date.next_visiting_date_time.isocalendar()[2]) - 1
        ) * 144 + 140

    # daily_hour_list
    daily_hour_list = list()

    try:
        if patient.daily_medication_count:
            if patient.daily_medication_count >= 1:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(patient.medication_noti_time_1.hour).zfill(2),
                        str(patient.medication_noti_time_1.minute).zfill(2),
                    )
                )

            if patient.daily_medication_count >= 2:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(patient.medication_noti_time_2.hour).zfill(2),
                        str(patient.medication_noti_time_2.minute).zfill(2),
                    )
                )

            if patient.daily_medication_count >= 3:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(patient.medication_noti_time_3.hour).zfill(2),
                        str(patient.medication_noti_time_3.minute).zfill(2),
                    )
                )

            if patient.daily_medication_count >= 4:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(patient.medication_noti_time_4.hour).zfill(2),
                        str(patient.medication_noti_time_4.minute).zfill(2),
                    )
                )

            if patient.daily_medication_count >= 5:
                daily_hour_list.append(
                    "{}:{}".format(
                        str(patient.medication_noti_time_5.hour).zfill(2),
                        str(patient.medication_noti_time_5.minute).zfill(2),
                    )
                )

    except AttributeError:
        daily_hour_list = ["재설정 필요"]

    # 달력
    datetime_list = get_now_ymd_list()
    year = int(picked_year)
    month = int(picked_month)
    day = [int(picked_day)]
    print_year = int(picked_year[2:4])

    date = datetime.datetime(year=year, month=month, day=1).date()
    day_of_month = calendar.monthrange(date.year, date.month)[1]
    day_list = []
    for i in range(1, day_of_month + 1):
        day_list.append(i)
    # 날짜의 시작 날짜인 1일을 무슨 요일에 시작하는지를 계산하여 달력에 표시
    day_of_the_week = datetime.date(
        year, month, 1
    ).weekday()  # weekday --> 날짜의 요일을 숫자로 출력
    day_of_the_week_list = []
    if day_of_the_week == 6:
        pass
    else:
        for j in range(day_of_the_week + 1):
            day_of_the_week_list.append(" ")

    weekday = weekInt_to_str((day_of_the_week + int(picked_day) - 1) % 7)

    # 내원 여부
    visit_list = []
    # 복약 성공 여부
    md_success_list = []
    md_delayed_success_list = []
    md_no_response_list = []
    md_failed_list = []
    md_side_effect_list = []

    for i in day_list:
        date_str = ""
        date_str += str(picked_year)
        date_str += ","
        date_str += str(picked_month)
        date_str += ","
        i = str(i)
        date_str += i
        date_str = get_date(date_str)
        dailyresult = MedicationResult.objects.filter(
            patient__code__contains=request.user.username, date=date_str
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
    # 오늘의 복약 정리
    date_str = ""
    date_str += str(picked_year)
    date_str += ","
    date_str += str(picked_month)
    date_str += ","
    date_str += str(picked_day)
    date_str = get_date(date_str)
    dailyresult = MedicationResult.objects.filter(
        patient__code__contains=request.user.username, date=date_str
    )
    today_md_success_list = []
    symptom_time_list = []
    symptom_name_list = []
    symptom_sev_list1 = []
    symptom_sev_list2 = []
    symptom_sev_list3 = []
    symptoms = []

    success_cnt = 1
    sideeffect_cnt = 1
    for i in dailyresult:
        if i.status == "SUCCESS":
            # 복약 성공 시간 출력 #
            if int(str(i.medication_time).split(":")[0]) == 12:
                med_time = (
                    "오후 "
                    + str(i.medication_time).split(":")[0]
                    + ":"
                    + str(i.medication_time).split(":")[1]
                )
            elif int(str(i.medication_time).split(":")[0]) >= 12:
                med_time = (
                    "오후 "
                    + str(int(str(i.medication_time).split(":")[0]) - 12)
                    + ":"
                    + str(i.medication_time).split(":")[1]
                )
            else:
                med_time = (
                    "오전 "
                    + str(i.medication_time).split(":")[0]
                    + ":"
                    + str(i.medication_time).split(":")[1]
                )

            text = str(success_cnt) + " : " + str(med_time)
            today_md_success_list.append(str(text))
            success_cnt += 1

        if i.status == "SIDE_EFFECT":
            # 부작용 기록은 곧 복약했음을 의미하기 때문에 복약 성공 시간도 출력함 #
            if int(str(i.medication_time).split(":")[0]) == 12:
                med_time = (
                    "오후 "
                    + str(i.medication_time).split(":")[0]
                    + ":"
                    + str(i.medication_time).split(":")[1]
                )
            elif int(str(i.medication_time).split(":")[0]) >= 12:
                med_time = (
                    "오후 "
                    + str(int(str(i.medication_time).split(":")[0]) - 12)
                    + ":"
                    + str(i.medication_time).split(":")[1]
                )
            else:
                med_time = (
                    "오전 "
                    + str(i.medication_time).split(":")[0]
                    + ":"
                    + str(i.medication_time).split(":")[1]
                )

            text = str(success_cnt) + " : " + str(med_time)
            today_md_success_list.append(str(text))
            success_cnt += 1

            # 부작용 출력 부분 #
            symptom_names = i.symptom_name.split(",")
            question1 = "얼마나 자주"
            question2 = "가장 심할 때"
            question3 = "일상에 지장"
            symptom_severity1s = i.symptom_severity1.split(",")
            symptom_severity2s = i.symptom_severity2.split(",")
            symptom_severity3s = i.symptom_severity3.split(",")
            symptom_num = len(symptom_names)

            for i in range(symptom_num):
                symptom_name_list.append(
                    "{} : {}".format(str(sideeffect_cnt), str(symptom_names[i]))
                )
                sideeffect_cnt += 1
                symptom_time_list.append("{}".format(str(med_time)))

                symptom_sev_list1.append(
                    "{}: {}".format(str(question1), str(symptom_severity1s[i]))
                )
                symptom_sev_list2.append(
                    "{}: {}".format(str(question2), str(symptom_severity2s[i]))
                )
                symptom_sev_list3.append(
                    "{}: {}".format(str(question3), str(symptom_severity3s[i]))
                )
                symptoms = zip(
                    symptom_name_list,
                    symptom_time_list,
                    symptom_sev_list1,
                    symptom_sev_list2,
                    symptom_sev_list3,
                )

    # 이전 월, 다음 월 달력
    next_year, next_month = get_next_month(month, year)
    prev_year, prev_month = get_prev_month(month, year)
    
    today_med_list = MedicationResult.objects.filter(
        patient__id__contains=pid, date=datetime.date.today(), status__in=["SUCCESS", "SIDE_EFFECT"]
    )

    context = {
        "nickname": nickname,
        "start_date": start_date,
        "end_date": end_date,
        "treat_started_date": patient.treatment_started_date,
        "treat_end_date": patient.treatment_end_date,
        "cure_progress": p_str,
        "med_progress": med_str,
        "patient": patient,
        "day_list": print_day_list(d),
        "daily_hour_list": daily_hour_list,
        "visiting_num": visiting_num,
        "prev_week": prev_week(d),
        "next_week": next_week(d),
        "prev_year": prev_year,
        "prev_month": int(prev_month),
        "next_month": int(next_month),
        "next_year": next_year,
        "year": year,
        "month": month,
        "day": day[0],
        "weekday": weekday,
        "print_year": print_year,
        "today": day,
        "day_list": day_list,
        "day_of_the_week_list": day_of_the_week_list,
        "visit_list": visit_list,
        "md_success_list": md_success_list,
        "md_delayed_success_list": md_delayed_success_list,
        "md_no_response_list": md_no_response_list,
        "md_failed_list": md_failed_list,
        "md_side_effect_list": md_side_effect_list,
        "today_md_success_list": today_md_success_list,
        "symptoms": symptoms,
        "med_cnt": med_cnt,
        "daily_med_fullfill": len(today_med_list) == patient.daily_medication_count,
    }
    return render(request, "patient_dashboard2.html", context=context)


@login_required(login_url="/", redirect_field_name="next")
def inspection_result(request):
    date_list = []
    type_list = []
    th_list = []
    res_list = []

    print(request.user.username)
    inspections = list(
        Sputum_Inspection.objects.filter(
            patient_set__code__contains=request.user.username
        )
    ) + list(
        Pcr_Inspection.objects.filter(patient_set__code__contains=request.user.username)
    )
    print(
        Sputum_Inspection.objects.filter(
            patient_set__code__contains=request.user.username
        )
    )
    inspections.sort(key=lambda x: x.insp_date, reverse=True)
    print(inspections)
    for insp in inspections:
        # 검사 날짜, 검사 종류, 검사 세부 분류, 검사 결과
        if hasattr(insp, "pcr_result"):
            date_list.append(
                "{}.{}.{}".format(
                    str(insp.insp_date.year)[2:4],
                    str(insp.insp_date.month).zfill(2),
                    str(insp.insp_date.day).zfill(2),
                )
            )
            type_list.append("PCR 검사")
            th_list.append("")
            res_list.append(insp.pcr_result)
        else:
            date_list.append(
                "{}.{}.{}".format(
                    str(insp.insp_date.year)[2:4],
                    str(insp.insp_date.month).zfill(2),
                    str(insp.insp_date.day).zfill(2),
                )
            )
            date_list.append(
                "{}.{}.{}".format(
                    str(insp.insp_date.year)[2:4],
                    str(insp.insp_date.month).zfill(2),
                    str(insp.insp_date.day).zfill(2),
                )
            )
            type_list.append("도말 검사")
            type_list.append("배양 검사")
            th_list.append(insp.th)
            th_list.append(insp.th)
            res_list.append(insp.smear_result)
            res_list.append(insp.culture_result)

    insp_zip = zip(date_list, type_list, th_list, res_list)

    context = {"insp_zip": insp_zip}
    return render(request, "patient_inspection.html", context=context)


def inspection_detail(request):
    return render(request, "inspection_detail.html")


def mailSend(msg):  # 메일전송 함수
    smtp_server = smtplib.SMTP(host="smtp.office365.com", port=587)
    smtp_server.ehlo()
    smtp_server.starttls()
    smtp_server.ehlo()
    smtp_server.login(os.environ.get("EMAIL_SENDER"), os.environ.get("PW_SENDER"))

    smtp_server.send_message(msg)  # 메세지 전송
    smtp_server.quit()  # stmp 종료

def debug_context(context: dict):
    for i in context:
        print(i, ":", context[i])
