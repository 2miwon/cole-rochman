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
