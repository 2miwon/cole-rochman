from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db1',
        'USER': 'sean0921',
        'PASSWORD': 'cjstmdqja',
        'HOST': 'csbdb1.c3q5bv2ohcbc.ap-northeast-2.rds.amazonaws.com',
        'PORT': 5432,
        'TEST': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'db1test',
            'USER': 'sean0921',
            'PASSWORD': 'cjstmdqja',
            'HOST': 'csbdb1test.c3q5bv2ohcbc.ap-northeast-2.rds.amazonaws.com',
            'PORT': 5432,
        },
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

LG_CNS = {
    "API_KEY": "",
    "CHANNEL_ID": "",
    "SERVICE_NO": 0
}
AUTO_SEND_NOTIFICAITON = False