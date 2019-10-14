from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import PatientCreate, TestView, ValidatePatientCode, MediacationNotificationTest

urlpatterns = [
    path('patients/', PatientCreate.as_view(), name='patient-create'),
    path('test/', TestView.as_view(), name='test'),
    path('test/skill/', MediacationNotificationTest.as_view(), name='test-skill'),
    path('validate/patient/code/', ValidatePatientCode.as_view(), name='validate-patient-code'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
