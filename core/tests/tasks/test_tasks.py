import datetime
from unittest import mock

from rest_framework.test import APITestCase

from core.models import NotificationRecord
from core.tasks.notification import _create_morning_notification, MORNING_NOTI_TIME
from core.tasks.util.biz_message import TYPE
from core.tests.factory.patients import CompletePatientFactory


class NotificationTest(APITestCase):
    def test_create_morning_notification_success(self):
        p = CompletePatientFactory()
        _create_morning_notification()
        # self.assertEqual(result['success_count'], 0)

        nr = NotificationRecord.objects.first()
        self.assertEqual(nr.patient, p)
        self.assertEqual(nr.biz_message_type, TYPE.MORNING_MEDI_MANAGEMENT_TRUE.value)
        self.assertEqual(nr.get_status(), nr.STATUS.PENDING)
        self.assertEqual(nr.recipient_number, p.phone_number)
        self.assertEqual(nr.send_at.astimezone(),
                         datetime.datetime.combine(datetime.datetime.today(), MORNING_NOTI_TIME).astimezone())

    # @mock.patch('core.api.tasks.notification_record.TODAY', mock.MagicMock(return_value=datetime.time(hour=9)))
    # def check_sendable(self):
    #     p = CompletePatientFactory()
    #     _create_morning_notification()