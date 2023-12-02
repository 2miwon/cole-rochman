from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    name = "core"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        if settings.AUTO_SEND_NOTIFICAITON:
            from . import runapscheduler

            # runapscheduler.start()
