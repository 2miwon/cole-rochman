from django.db import models

from core.tasks.util.biz_message import TYPE as BIZ_MESSAGE_TYPE
from core.models.helper.helper import EnumField
from core.util.dayModule import get_today


class NotificationTime(models.Model):
    class Meta:
        verbose_name = "복약 알림 시간"
        verbose_name_plural = "복약 알림 시간"

    class TYPE(EnumField):
        MEDICATION_NOTI = "MEDICATION_NOTI"
        VISIT_NOTI = "VISIT_NOTI"

    patient = models.ForeignKey(
        "Patient",
        on_delete=models.SET_NULL,
        related_name="notification_time_tables",
        blank=True,
        null=True,
    )
    notification_time = models.DateTimeField()
    daily_num = models.IntegerField(
        verbose_name="복약 번호", default=1
    )  # 0 = reminder, 1 = 1회차, 2 = 2회차...
    activate = models.BooleanField(
        verbose_name="알림 활성화 여부", blank=False, null=False, default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    msg_type = models.CharField(
        max_length=20, choices=TYPE.choices(), default=TYPE.MEDICATION_NOTI.value
    )

    #
    # WTF !!!!!!!!!!!!!!!
    #
    def send(self) -> bool:
        import traceback
        from core.tasks.util.bizppurio.bizppurio import BizppurioRequest

        try:
            payload = self.build_biz_message_request()
        except:
            # self.result = traceback.format_exc()
            return False
        if not self.activate:
            return False
        success, result = BizppurioRequest(payload=payload).send()

        if success:
            self.set_delivered()
        elif self.tries_left > 0:
            self.set_retry()
        else:
            self.set_failed()

        self.result = result
        self.save()
        return success

    def build_biz_message_request(self):
        from core.tasks.util.biz_message import BizMessageBuilder

        biz_message = BizMessageBuilder(
            message_type=BIZ_MESSAGE_TYPE[self.msg_type],
            patient=self.patient,
            date=get_today(),
            noti_time_num=self.daily_num,
        )
        return biz_message.to_dict()
