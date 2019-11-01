from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from core.api.views.medications import PatientMedicationNotiTimeStart, PatientMedicationNotiSetTime, \
    PatientMedicationNotiReset
from core.api.views.patient_validations import ValidatePatientCode
from core.api.views.patients import PatientCreate, PatientUpdate, TestView
from core.api.views.visit_validations import ValidateTimeBefore
from core.api.views.visits import PatientVisitDateSet, PatientVisitNotiTimeBefore, PatientVisitStart

urlpatterns = [
    path('patients/create/', PatientCreate.as_view(), name='patient-create'),
    path('patients/update/', PatientUpdate.as_view(), name='patient-update'),
    path('patients/medication/noti/time/start/', PatientMedicationNotiTimeStart.as_view(), name='patient-medication-noti-time-start'),
    path('patients/medication/noti/time/set/', PatientMedicationNotiSetTime.as_view(), name='patient-medication-noti-set-time'),
    path('patients/medication/noti/reset/', PatientMedicationNotiReset.as_view(), name='patient-medication-noti-reset'),
    path('patients/visit/start/', PatientVisitStart.as_view(), name='patient-visit-start'),
    path('patients/visit/date/set/', PatientVisitDateSet.as_view(), name='patient-visit-date-set'),
    path('patients/visit/noti/time/', PatientVisitNotiTimeBefore.as_view(), name='patient-visit-noti-time'),
    path('validate/patient/code/', ValidatePatientCode.as_view(), name='validate-patient-code'),
    path('validate/time-before/', ValidateTimeBefore.as_view(), name='validate-time-before'),
    path('test/', TestView.as_view(), name='test'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
