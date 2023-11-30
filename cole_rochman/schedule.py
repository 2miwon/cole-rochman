from celery.schedules import crontab
from django.conf import settings
from core.util.dayModule import *

RETRY_OPTIONS = {
    "retry": True,
    "retry_policy": {
        "max_retries": 2,
        "interval_start": 1 * MINUTES,
        "interval_max": 1 * MINUTES,
    },
}

QUEUE_NOTIFICATION = {"queue": "default"}

# Morning Noti를 만드는  함수를 매일 00시 30분에 자동실행
# Medication Noti, Visit Noti를 만드는 함수를 매일 00시 40분에 자동실행
# 그날 전송해야 하는 알림톡 정보를 다 받아와서 저장하는 역할
SCHEDULE = {
    # "create-morning-notification-every-12-30-am": {
    #     "task": "core.tasks.notification.create_morning_notification",
    #     "schedule": crontab(minute=30, hour=0),
    #     "options": {**RETRY_OPTIONS, **QUEUE_NOTIFICATION},
    # },
    "create-medication-notification-every-12-40-am": {
        "task": "core.tasks.notification.create_medication_notification",
        "schedule": crontab(minute=40, hour=0),
        "options": {**RETRY_OPTIONS, **QUEUE_NOTIFICATION},
    },
    "create-medication-notification-every-12-40-am": {
        "task": "core.tasks.notification.create_medication_notification",
        "schedule": crontab(minute=40, hour=1),
        "options": {**RETRY_OPTIONS, **QUEUE_NOTIFICATION},
    },
    "create-visit-notification-every-12-40-am": {
        "task": "core.tasks.notification.create_visit_notification",
        "schedule": crontab(minute=40, hour=0),
        "options": {**RETRY_OPTIONS, **QUEUE_NOTIFICATION},
    },
}

# 매분 실행할 Notification 코드가 있는지 확인하고 실행함
# 저장해놓은 알림톡 정보를 바탕으로 해당 시간이 되면 알림톡을 전송하는 역할
if settings.AUTO_SEND_NOTIFICAITON:
    SCHEDULE.update(
        {
            "send-notification-every-1-minutes": {
                "task": "core.tasks.notification.send_notifications",
                "schedule": crontab(),
                "options": {**RETRY_OPTIONS, **QUEUE_NOTIFICATION},
            }
        }
    )
    # SCHEDULE.update({
    #     'send-notification-at=8-pm': {
    #         'task': 'core.tasks.notification.send_notifications',
    #         'schedule': crontab(minute=0, hour=20),
    #         'options': {**RETRY_OPTIONS, **QUEUE_NOTIFICATION}
    #     }
    # })
