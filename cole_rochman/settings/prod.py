from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = False

#ALLOWED_HOSTS = secrets.get('ALLOWED_HOST')
ALLOWED_HOSTS = ['43.200.26.183']

DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db2',
        'USER': 'postgres',
        'PASSWORD': 'cjstmdqja',
        'HOST': 'csbdb2.c3q5bv2ohcbc.ap-northeast-2.rds.amazonaws.com',
        'PORT': '5432',
        'TEST': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'db2test',
            'USER': 'postgres',
            'PASSWORD': 'cjstmdqja',
            'HOST': 'csbdb2test.c3q5bv2ohcbc.ap-northeast-2.rds.amazonaws.com',
            'PORT': '5432',
        }
    },
}
#    'default': secrets.get('DB_SETTINGS').get('PRODUCTION')

# noinspection PyUnresolvedReferences
STATIC_ROOT = '/var/www/cole-rochman/static/'

sentry_sdk.init(
    dsn=secrets.get('SENTRY_ADDRESS'),
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
            'address': secrets.get('PAPERTRAIL_ADDRESS')
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

BROKER_URL = secrets.get('REDIS_ADDRESS')

LG_CNS = secrets.get('LG_CNS')
AUTO_SEND_NOTIFICAITON = True
