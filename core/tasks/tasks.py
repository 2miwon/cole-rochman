import datetime

from celery import states
from django.db.models import Q

from cole_rochman.celery import app
from core.models import Patient
from core.serializers import NotificationRecordSerializer
from core.tasks.notification import MORNING_NOTI_TIME
from core.tasks.util.biz_message import TYPE


@app.task(bind=True)
def register_today_morning_notifications(self):
    sending_type = TYPE

    self.update_state(state=states.RECEIVED)

    # get targets
    queryset = Patient.objects.all()
    medications = Q(medication_manage_flag=True, medication_noti_flag=True)
    visits = Q(visit_manage_flag=True, visit_noti_flag=True)
    patients = queryset.filter(medications | visits).all()

    # loop in each target
    # create notification by target's morning notification type
    for patient in patients:
        type = sending_type(patient)
        data = {
            'patient': self.patient,
            'biz_message_type': type,
            'recipient_number': self.patient.phone_number,
            'send_at': datetime.datetime.combine(datetime.date.today(), MORNING_NOTI_TIME),
        }
        serializer = NotificationRecordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        notification_record = serializer.save()
        notification_record.build_biz_message_request()
