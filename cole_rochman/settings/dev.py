# dev.py 파일은 서버에서 테스트해보는 코드

from .base import *

DEBUG = True

ALLOWED_HOSTS = ["www.cole-rochman.co.kr", "localhost"]

# 실제 데이터베이스가 아님
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_db1',
        'USER': 'sean0921',
        'PASSWORD': 'cjstmdqja',
        'HOST': 'csbdb1.c3q5bv2ohcbc.ap-northeast-2.rds.amazonaws.com',
        'PORT': 5432,
    },
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

