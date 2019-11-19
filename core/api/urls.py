from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from core.api.views.general import ResponseAlwaysOK
from core.api.views.measurements import PatientMeasurementEntrance, MeasurementResultCreate, \
    PatientMeasurementNotiTimeQuestion, PatientMeasurementNotiSetTime, PatientMeasurementRestart, \
    PatientMeasurementNotiReset
from core.api.views.medications import PatientMedicationNotiTimeQuestion, PatientMedicationNotiSetTime, \
    PatientMedicationNotiReset, PatientMedicationEntrance, PatientMedicationRestart, \
    PatientMedicationNotiSetTimeInRestart, \
    PatientMedicationNotiTimeQuestionRestart
from core.api.views.medications_notification import PastMedicationCheckChooseTime
from core.api.views.temp import TempPatientDestroy
from core.api.views.validation_hospitals import ValidateHospitalCode
from core.api.views.validation_measurement_result import ValidateMeasurementResultOxygenSaturation
from core.api.views.validation_patients import ValidatePatientNickname, ValidatePatientCode
from core.api.views.patients import PatientCreateStart, PatientCreate, PatientUpdate, PatientInfo
from core.api.views.validation_visits import ValidateTimeBefore
from core.api.views.visits import PatientVisitDateSet, PatientVisitNotiTimeBefore, PatientVisitStart, \
    PatientVisitRestart

urlpatterns = [
    path('patients/create/start/', PatientCreateStart.as_view(), name='patient-create-start'),
    path('patients/create/', PatientCreate.as_view(), name='patient-create'),
    path('patients/update/', PatientUpdate.as_view(), name='patient-update'),
    path('patients/info/', PatientInfo.as_view(), name='patient-info'),
    path('patients/medication/start/', PatientMedicationEntrance.as_view(), name='patient-medication-start'),
    path('patients/medication/noti/time/question/', PatientMedicationNotiTimeQuestion.as_view(),
         name='patient-medication-noti-time-question'),
    path('patients/medication/noti/time/question/restart/', PatientMedicationNotiTimeQuestionRestart.as_view(),
         name='patient-medication-noti-time-question-restart'),
    path('patients/medication/noti/time/set/', PatientMedicationNotiSetTime.as_view(),
         name='patient-medication-noti-set-time'),
    path('patients/medication/noti/time/set/restart/', PatientMedicationNotiSetTimeInRestart.as_view(),
         name='patient-medication-noti-set-time-in-restart'),
    path('patients/medication/noti/reset/', PatientMedicationNotiReset.as_view(), name='patient-medication-noti-reset'),
    path('patients/medication/restart/', PatientMedicationRestart.as_view(), name='patient-medication-restart'),
    path('patients/medication/past-check/choose-time/', PastMedicationCheckChooseTime.as_view(),
         name='patients-medication-past-check-choose-time'),
    path('patients/visit/start/', PatientVisitStart.as_view(), name='patient-visit-start'),
    path('patients/visit/date/set/', PatientVisitDateSet.as_view(), name='patient-visit-date-set'),
    path('patients/visit/noti/time/', PatientVisitNotiTimeBefore.as_view(), name='patient-visit-noti-time'),
    path('patients/visit/restart/', PatientVisitRestart.as_view(), name='patient-visit-restart'),
    path('patients/measurement/entrance/', PatientMeasurementEntrance.as_view(), name='patient-measurement-entrance'),
    path('patients/measurement/noti/time/question/', PatientMeasurementNotiTimeQuestion.as_view(),
         name='patient-measurement-noti-time-question'),
    path('patients/measurement/noti/time/set/', PatientMeasurementNotiSetTime.as_view(),
         name='patient-measurement-noti-set-time'),
    path('patients/measurement-result/create/', MeasurementResultCreate.as_view(), name='patient-measurement-create'),
    path('patients/measurement/restart/', PatientMeasurementRestart.as_view(), name='patient-measurement-restart'),
    path('patients/measurement/noti/reset/', PatientMeasurementNotiReset.as_view(),
         name='patient-measurement-noti-reset'),
    path('temp/patient/delete/', TempPatientDestroy.as_view(), name='temp-patient-destroy'),
    path('validate/patient/code/', ValidatePatientCode.as_view(), name='validate-patient-code'),
    path('validate/patient/nickname/', ValidatePatientNickname.as_view(), name='validate-patient-nickname'),
    path('validate/hospital/code/', ValidateHospitalCode.as_view(), name='validate-hospital-code'),
    path('validate/time-before/', ValidateTimeBefore.as_view(), name='validate-time-before'),
    path('validate/measurement-result/oxygen-saturation/', ValidateMeasurementResultOxygenSaturation.as_view(),
         name='validate-measurement-result-oxygen-saturation'),
    path('general/response-always-ok/', ResponseAlwaysOK.as_view(),
         name='general-response-always-ok'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
