from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'colerochman_dev',
        'USER': 'colerochman',
        'PASSWORD': 'colerochman',
        'PORT': 5432,
        'TEST': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'colerochman_test',
            'USER': 'colerochman',
            'PASSWORD': 'colerochman',
            'PORT': 5432,
        },
    },
}
