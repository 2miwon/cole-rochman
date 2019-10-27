from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = False

ALLOWED_HOSTS = secrets['ALLOWED_HOST']

DATABASES = {
    'default': secrets['DB_SETTINGS']['PRODUCTION']
}

STATIC_ROOT = '/var/www/cole-rochman/static/'

sentry_sdk.init(
    dsn=secrets['SENTRY_ADDRESS'],
    integrations=[DjangoIntegration()],
    environment='production'
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s SENDER_NAME PROGRAM_NAME: %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(PROJECT_DIR, 'settings/debug.log'),
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
        'SysLog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'simple',
            'address': ('logs2.papertrailapp.com', 50435)
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file', 'SysLog'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


