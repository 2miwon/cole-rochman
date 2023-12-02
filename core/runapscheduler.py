# import logging
import datetime

from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore
from apscheduler.triggers.cron import CronTrigger
from core.models import Patient, NotificationRecord, NotificationTime
from core.serializers import NotificationRecordSerializer
from core.tasks.util.biz_message import TYPE

# from core.tasks.notification import *
from django.conf import settings


# logger = logging.getLogger(__name__)


def start():
    def handle(self, *args, **options):
        print("debug:: start scheduler")
        scheduler = BackgroundScheduler(
            timezone=settings.TIME_ZONE, coalesce=True, max_instances=1
        )
        # scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            create_medication_noti_aps,
            trigger=CronTrigger(hour="0", minute="40"),  # 실행 시간입니다.
            id="create-medication-notification-every-12-40-am",
            max_instances=1,
            replace_existing=True,
        )
        # logger.info("Added job 'create-medication-notification-every-12-40-am'.")

        scheduler.add_job(
            create_visit_noti_aps,
            trigger=CronTrigger(hour="0", minute="40"),
            id="create-visit-notification-every-12-40-am",  # id는 고유해야합니다.
            max_instances=1,
            replace_existing=True,
        )

        scheduler.add_job(
            send_noti_aps,
            trigger=CronTrigger(minute="*"),
            id="send-notification-every-1-minutes",  # id는 고유해야합니다.
            max_instances=1,
            replace_existing=True,
        )

        # logger.info("Added job 'send-notification-every-1-minutes'.")

        # scheduler.add_job(
        #     elastic_send_noti_aps,
        #     trigger=CronTrigger(minute="*"),
        #     id="send-elastic-notification-every-1-minutes",  # id는 고유해야합니다.
        #     max_instances=1,
        #     replace_existing=True,
        # )

        try:
            # logger.info("Starting scheduler...")
            scheduler.start()  # 없으면 동작하지 않습니다.
        except KeyboardInterrupt:
            # logger.info("Stopping scheduler...")
            scheduler.shutdown()
            # logger.info("Scheduler shut down successfully!")


def create_medication_noti_aps():
    print("debug:: invoke create medication notification")
    patients = Patient.objects.all()
    result = {"patient_counts": len(patients)}
    for patient in patients:
        if not patient.is_medication_noti_sendable():
            continue
        for noti_time_num, noti_time in enumerate(patient.medication_noti_time_list()):
            if noti_time is None:
                continue
            medication_result = patient.create_medication_result(
                noti_time_num=noti_time_num + 1
            )
            if medication_result:
                medication_result.create_notification_record(
                    noti_time_num=noti_time_num + 1
                )
                result["created_count"] = (result.get("created_count") or 0) + 1
    return result


def create_visit_noti_aps():
    print("debug:: invoke create visit notification")
    patients = Patient.objects.all()
    result = {"patient_counts": len(patients)}

    for patient in patients:
        if (
            not patient.is_visit_noti_sendable()
            or not patient.visit_notification_before
            or patient.next_visiting_date_time is None
        ):
            continue

        noti_date_time = patient.next_visiting_date_time - datetime.timedelta(
            seconds=patient.visit_notification_before
        )
        if noti_date_time.date() == datetime.datetime.today():
            data = {
                "patient": patient.pk,
                "biz_message_type": TYPE.VISIT_NOTI.value,
                "recipient_number": patient.phone_number,
                "send_at": noti_date_time,
            }
            serializer = NotificationRecordSerializer(data=data)
            if serializer.is_valid():
                notification_record = serializer.save()
                notification_record.build_biz_message_request()
                notification_record.save()
                result["created_count"] = (result.get("created_count") or 0) + 1
    return result


def send_noti_aps():
    print("debug:: invoke notification at ", datetime.datetime.now().astimezone())
    now = datetime.datetime.now().astimezone()
    time_range = [now - datetime.timedelta(minutes=1), now]
    notifications = NotificationRecord.objects.filter(
        status__in=[NotificationRecord.STATUS.PENDING, NotificationRecord.STATUS.RETRY],
        tries_left__gt=0,
        send_at__range=time_range,
    ).all()
    result = {"notifications_counts": len(notifications), "sent_count": 0}
    for noti in notifications:
        success = noti.send()
        if success:
            result["sent_count"] += 1
    if result["sent_count"]:
        print("debug:: send notification")
    return result


def elastic_send_noti_aps():
    print("debug:: invoke elastic noti at ", datetime.datetime.now().astimezone())
    now = datetime.datetime.now().astimezone()
    time_range = [now - datetime.timedelta(minutes=1), now]

    time_table = NotificationTime.objects.filter(
        notification_time__range=time_range,
    ).all()
    result = {"notifications_counts": len(time_table), "sent_count": 0}
    for noti in time_table:
        success = noti.send()
        if success:
            result["sent_count"] += 1
    if result["sent_count"]:
        print("debug:: send notification")
    return result
