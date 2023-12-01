from django.apps import AppConfig
from django.conf import settings

class CoreConfig(AppConfig):
    name = 'core'

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        if settings.SCHEDULER_DEFAULT:
            from . import runapscheduler
            runapscheduler.start()