# dev.py 파일은 서버에서 테스트해보는 코드

from .base import *

DEBUG = True

ALLOWED_HOSTS = ["www.cole-rochman.co.kr", "localhost"]

# 실제 데이터베이스가 아님
DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'colerochman_dev',
    #     'USER': 'colerochman',
    #     'PASSWORD': 'colerochman',
    #     'PORT': 5432,
    #     'TEST': {
    #         'ENGINE': 'django.db.backends.postgresql',
    #         'NAME': 'colerochman_test',
    #         'USER': 'colerochman',
    #         'PASSWORD': 'colerochman',
    #         'PORT': 5432,
    #     },
    # },
    'default': secrets.get('DB_SETTINGS')["TEST"]
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(PROJECT_DIR, 'settings/debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}



BROKER_URL = 'redis://localhost:6380/0'

AUTO_SEND_NOTIFICAITON = True 

