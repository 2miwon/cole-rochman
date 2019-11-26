from celery.schedules import crontab

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
    'create_morning_notification-every-12-30': {
        'task': 'core.tasks.notification.create_morning_notification',
        'schedule': crontab(minute=30, hour=12),
        'options': {**RETRY_OPTIONS, **QUEUE_NOTIFICATION}
    },
    'create_medication_notification-every-12-40': {
        'task': 'core.tasks.notification.create_medication_notification',
        'schedule': crontab(minute=40, hour=12),
        'options': {**RETRY_OPTIONS, **QUEUE_NOTIFICATION}
    },
    'create_visit_notification-every-12-40': {
        'task': 'core.tasks.notification.create_visit_notification',
        'schedule': crontab(minute=40, hour=12),
        'options': {**RETRY_OPTIONS, **QUEUE_NOTIFICATION}
    },
    'create_measurement_notification-every-12-40': {
        'task': 'core.tasks.notification.create_measurement_notification',
        'schedule': crontab(minute=40, hour=12),
        'options': {**RETRY_OPTIONS, **QUEUE_NOTIFICATION}
    },
}
