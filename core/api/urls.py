from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import PatientCreate, PatientUpdate, TestView, ValidatePatientCode, PatientMediacationNotiSetTime

urlpatterns = [
    path('patients/create/', PatientCreate.as_view(), name='patient-create'),
    path('patients/update/', PatientUpdate.as_view(), name='patient-update'),
    path('patients/medication/time/', PatientMediacationNotiSetTime.as_view(), name='patient-medication-noti-time'),
    path('test/', TestView.as_view(), name='test'),
    path('validate/patient/code/', ValidatePatientCode.as_view(), name='validate-patient-code'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
