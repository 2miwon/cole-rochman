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
    'queue': 'notification'
}

SCHEDULE = {
    'create-morning-notification-every-12-30-am': {
        'task': 'core.tasks.notification.create_morning_notification',
        'schedule': crontab(minute=30, hour=0),
        'options': {**RETRY_OPTIONS, **QUEUE_NOTIFICATION}
    },
    'create-medication-notification-every-12-40-am': {
        'task': 'core.tasks.notification.create_medication_notification',
        'schedule': crontab(minute=40, hour=0),
        'options': {**RETRY_OPTIONS, **QUEUE_NOTIFICATION}
    },
    'create-visit-notification-every-12-40-am': {
        'task': 'core.tasks.notification.create_visit_notification',
        'schedule': crontab(minute=40, hour=0),
        'options': {**RETRY_OPTIONS, **QUEUE_NOTIFICATION}
    },
    'create-measurement-notification-every-12-40-am': {
        'task': 'core.tasks.notification.create_measurement_notification',
        'schedule': crontab(minute=40, hour=0),
        'options': {**RETRY_OPTIONS, **QUEUE_NOTIFICATION}
    },
}

if settings.AUTO_SEND_NOTIFICAITON:
    SCHEDULE.update({
        'send-notification-every-5-minutes': {
            'task': 'core.tasks.notification.send_notifications',
            'schedule': crontab(minute='*/5', hour='7-20'),
            'options': {**RETRY_OPTIONS, **QUEUE_NOTIFICATION}
        }
    })