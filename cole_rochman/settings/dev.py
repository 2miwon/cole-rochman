from .base import *

ALLOWED_HOSTS = ['43.200.26.183']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db1',
        'USER': 'sean0921',
        'PASSWORD': 'cjstmdqja',
        'HOST': 'csbdb1.c3q5bv2ohcbc.ap-northeast-2.rds.amazonaws.com',
        'PORT': '5432',
        'TEST': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'db1test',
            'USER': 'sean0921',
            'PASSWORD': 'cjstmdqja',
            'HOST': 'csbdb1test.c3q5bv2ohcbc.ap-northeast-2.rds.amazonaws.com',
            'PORT': '5432',
        },
    },
}
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': 'colerochman_dev',
#        'USER': 'colerochman',
#        'PASSWORD': 'colerochman',
#        'PORT': 5432,
#        'TEST': {
#            'ENGINE': 'django.db.backends.postgresql',
#            'NAME': 'colerochman_test',
#            'USER': 'colerochman',
#            'PASSWORD': 'colerochman',
#            'PORT': 5432,
#        },
#    },

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



#BROKER_URL = 'redis://localhost:6379/0'
BROKER_URL = 'redis://csb-redis.dxfo66.ng.0001.apn2.cache.amazonaws.com:6379'

#LG_CNS = {
#    "API_KEY": ""
#    "CHANNEL_ID": "",
#    "SERVICE_NO": 0
#}

AUTO_SEND_NOTIFICAITON = True
