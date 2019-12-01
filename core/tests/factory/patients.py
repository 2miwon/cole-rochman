import datetime

import factory

from core.models import Patient
from core.tests.factory.hospital import HospitalFactory

MINUTES = 60
HOURS = 60 * MINUTES
DAYS = 24 * HOURS


class PatientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Patient

    code = factory.Sequence(lambda n: 'A001%s' % str(n).zfill(8))
    hospital = factory.LazyFunction(HospitalFactory)
    kakao_user_id = factory.Faker('sha256')
    nickname = factory.Faker('first_name')
    user = None
    treatment_started_date = datetime.datetime.today().astimezone() - datetime.timedelta(days=10)


class MedicationPatientFactory(PatientFactory):
    medication_manage_flag = True
    daily_medication_count = 3
    medication_noti_flag = True
    medication_noti_time_1 = datetime.time(hour=8)
    medication_noti_time_2 = datetime.time(hour=10)
    medication_noti_time_3 = datetime.time(hour=12)


class VisitPatientFactory(PatientFactory):
    visit_manage_flag = True
    visit_notification_flag = True
    next_visiting_date_time = datetime.datetime.today().astimezone() + datetime.timedelta(days=10)
    visit_notification_before = 1 * DAYS


class MeasurementPatientFactory(PatientFactory):
    measurement_manage_flag = True
    daily_measurement_count = 3
    measurement_noti_flag = True
    measurement_noti_time_1 = datetime.time(hour=8)
    measurement_noti_time_2 = datetime.time(hour=10)
    measurement_noti_time_3 = datetime.time(hour=12)


class VisitTodayPatientFactory(VisitPatientFactory):
    next_visiting_date_time = datetime.datetime.today().astimezone()
    visit_notification_before = 3 * HOURS


class CompletePatientFactory(MedicationPatientFactory, VisitPatientFactory, MeasurementPatientFactory):
    phone_number = factory.Sequence(lambda n: '010%s' % str(n).zfill(8))
    name = factory.LazyAttribute(lambda obj: '%s' % obj.nickname[:5])
