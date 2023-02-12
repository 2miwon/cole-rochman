from celery.schedules import crontab
from django.conf import settings

MINUTES = 60
HOURS = 60 * MINUTES
DAYS = 24 * HOURS

RETRY_OPTIONS = {
    'retry': True,
    'retry_policy': {
        'max_retries': 2,
        'interval_start': 1 * MINUTES,
        'interval_max': 1 * MINUTES,
    }
}

QUEUE_NOTIFICATION = {
    'queue': 'default'
}


SCHEDULE = {
    'create-morning-notification-every-12-30-am': {
        'task': 'core.tasks.notification.create_morning_notification',
        'schedule': crontab(minute=40, hour=7),
        'options': {**RETRY_OPTIONS, **QUEUE_NOTIFICATION}
    },
    'create-medication-notification-every-12-40-am': {
        'task': 'core.tasks.notification.create_medication_notification',
        'schedule': crontab(minute=50, hour=7),
        'options': {**RETRY_OPTIONS, **QUEUE_NOTIFICATION}
    },
    'create-visit-notification-every-12-40-am': {
        'task': 'core.tasks.notification.create_visit_notification',
        'schedule': crontab(minute=50, hour=7),
        'options': {**RETRY_OPTIONS, **QUEUE_NOTIFICATION}
    }
}

if settings.AUTO_SEND_NOTIFICAITON:
    SCHEDULE.update({
        'send-notification-every-1-minutes': {
            'task': 'core.tasks.notification.send_notifications',
            'schedule': crontab(minute='*/1', hour='7-19'),
            'options': {**RETRY_OPTIONS, **QUEUE_NOTIFICATION}
        }
    })
    SCHEDULE.update({
        'send-notification-at=8-pm': {
            'task': 'core.tasks.notification.send_notifications',
            'schedule': crontab(minute=0, hour=20),
            'options': {**RETRY_OPTIONS, **QUEUE_NOTIFICATION}
        }
    })
