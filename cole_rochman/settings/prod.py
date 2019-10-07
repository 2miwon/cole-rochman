from .base import *

DEBUG = False

ALLOWED_HOSTS = ['ec2-13-209-68-166.ap-northeast-2.compute.amazonaws.com']

DATABASES = {
    'default': secrets['DB_SETTINGS']['PRODUCTION']
}

STATIC_ROOT = '/var/www/cole-rochman/static/'
