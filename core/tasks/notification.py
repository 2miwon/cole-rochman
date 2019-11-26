import datetime

from cole_rochman.celery import app
from core.models import Patient, NotificationRecord
from core.serializers import NotificationRecordSerializer
from core.tasks.util.biz_message import TYPE

MORNING_NOTI_TIME = datetime.time(hour=8)  # originally 7, but temporarily 8 due to limitation by Kakao's policy


@app.tasks(bind=True)
def create_morning_notification():
    patients = Patient.objects.all()
    for patient in patients:
        if not patient.phone_number:
            continue
        type = TYPE.get_morning_noti_type(patient)
        reserve_time = datetime.datetime.combine(datetime.date.today(), MORNING_NOTI_TIME).strftime('%Y-%m-%d %H:%M')

        data = {
            'patient': patient.pk,
            'biz_message_type': type.value,
            'recipient_number': patient.phone_number,
            'send_at': reserve_time
        }
        serializer = NotificationRecordSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            notification_record = serializer.save()
            notification_record.build_biz_message_request()
            notification_record.save()


@app.tasks(bind=True)
def create_medication_notification():
    patients = Patient.objects.all()
    for patient in patients:
        if not patient.is_medication_noti_sendable():
            continue

        for noti_time_num, noti_time in enumerate(patient.medication_noti_time_list()):
            if noti_time is None:
                continue
            medication_result = patient.create_medication_result(noti_time_num=noti_time_num)
            if medication_result:
                medication_result.create_notification_record(noti_time_num=noti_time_num)


@app.tasks(bind=True)
def create_visit_notification():
    patients = Patient.objects.all()
    for patient in patients:
        if not patient.is_visit_noti_sendable() or patient.visit_notification_before == 0:
            continue

        noti_date_time = patient.next_visiting_date_time - datetime.timedelta(seconds=patient.visit_notification_before)
        if noti_date_time.date() == datetime.datetime.today():
            data = {
                'patient': patient.pk,
                'biz_message_type': TYPE.VISIT_NOTI.value,
                'recipient_number': patient.phone_number,
                'send_at': noti_date_time
            }
            serializer = NotificationRecordSerializer(data=data)
            if serializer.is_valid():
                notification_record = serializer.save()
                notification_record.build_biz_message_request()
                notification_record.save()


@app.tasks(bind=True)
def create_measurement_notification():
    patients = Patient.objects.all()
    for patient in patients:
        if not patient.is_measurement_noti_sendable():
            continue

        for noti_time_num, noti_time in enumerate(patient.medication_noti_time_list()):
            if noti_time is None:
                continue
            measurement_result = patient.create_measurement_result(noti_time_num=noti_time_num)
            if measurement_result:
                measurement_result.create_notification_record()


@app.tasks(bind=True)
def send_notifications():
    notifications = NotificationRecord.objects.filter(status=NotificationRecord.STATUS.PENDING).all()
    for noti in notifications:
        noti.send()
