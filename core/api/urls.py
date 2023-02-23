from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from core.api.views.general import ResponseAlwaysOK
from core.api.views.measurements import PatientMeasurementEntrance, PatientMeasurementNotiTimeQuestion, PatientMeasurementNotiSetTime, PatientMeasurementRestart, PatientMeasurementNotiReset
from core.api.views.measurements_notification import MeasurementResultCheck, MeasurementResultCheckFromNotification
from core.api.views.medications import PatientMedicationNotiTimeQuestion, PatientMedicationNotiSetTime, PatientMedicationNotiReset, PatientMedicationEntrance, PatientMedicationRestart
from core.api.views.medications_notification import PastMedicationSuccess, PastMedicationFailed, PastMedicationEntrance, PastMedicationSideEffect_N01, PastMedicationSideEffect_N02, PastMedicationSideEffect_N03, PastMedicationSideEffect_N04, PastMedicationSideEffect_N05, PastMedicationSideEffect_N06, PastMedicationSideEffect_N07, PastMedicationSideEffect_N08, PastMedicationSideEffect_N09, PastMedicationSideEffect_N10, PastMedicationSideEffect_N11 
from core.api.views.temp import TempPatientDestroy
from core.api.views.validation_hospitals import ValidateHospitalCode
from core.api.views.validation_measurements_notification import ValidateMeasurementResultOxygenSaturation
from core.api.views.validation_patients import ValidatePatientNickname, ValidatePatientName, ValidatePatientPhone, ValidatePatientCode, ValidatePatientPassword, ValidatePatientWeight, ValidatePatientVision
from core.api.views.patients import PatientCreateStart, PatientCreate, PatientUpdate, PatientInfo, PatientSafeOut, PatientWeight, PatientVision, PatientCodePrint
from core.api.views.validation_visits import ValidateTimeBefore
from core.api.views.visits import PatientVisitDateSet, PatientVisitNotiTimeBefore, PatientVisitStart, PatientVisitRestart
from core.api.views.guardian import GuardianCreateStart, GuardianCreate, GuardianPhone, GuardianCheckPatientMedication

urlpatterns = [
    path('patients/create/start/', PatientCreateStart.as_view(), name='patient-create-start'),
    path('patients/create/', PatientCreate.as_view(), name='patient-create'),
    path('patients/update/', PatientUpdate.as_view(), name='patient-update'),
    path('patients/info/', PatientInfo.as_view(), name='patient-info'),
    path('patients/medication/start/', PatientMedicationEntrance.as_view(), name='patient-medication-start'),
    path('patients/medication/noti/time/question/', PatientMedicationNotiTimeQuestion.as_view(),
         name='patient-medication-noti-time-question'),
    path('patients/medication/noti/time/set/', PatientMedicationNotiSetTime.as_view(),
         name='patient-medication-noti-set-time'),
    path('patients/medication/noti/reset/', PatientMedicationNotiReset.as_view(), name='patient-medication-noti-reset'),
    path('patients/medication/restart/', PatientMedicationRestart.as_view(), name='patient-medication-restart'),
#    path('patients/medication/past-check/choose-time/', PastMedicationCheckChooseTime.as_view(),
#         name='patients-medication-past-check-choose-time'),
    path('patients/medication/past-check/entrance/', PastMedicationEntrance.as_view(),
         name='patients-medication-past-entrance'),
    path('patients/medication/past-check/success/', PastMedicationSuccess.as_view(),
         name='patients-medication-past-check-success'),
    path('patients/medication/past-check/failed/', PastMedicationFailed.as_view(),
         name='patients-medication-past-check-failed'),
    path('patients/medication/past-check/side-effect_N01/', PastMedicationSideEffect_N01.as_view(),
         name='patients-medication-past-check-side-effect-n01'),
    path('patients/medication/past-check/side-effect_N02/', PastMedicationSideEffect_N02.as_view(),
         name='patients-medication-past-check-side-effect-n02'),
    path('patients/medication/past-check/side-effect_N03/', PastMedicationSideEffect_N03.as_view(),
         name='patients-medication-past-check-side-effect-n03'),
    path('patients/medication/past-check/side-effect_N04/', PastMedicationSideEffect_N04.as_view(),
         name='patients-medication-past-check-side-effect-n04'),
    path('patients/medication/past-check/side-effect_N05/', PastMedicationSideEffect_N05.as_view(),
         name='patients-medication-past-check-side-effect-n05'),
    path('patients/medication/past-check/side-effect_N06/', PastMedicationSideEffect_N06.as_view(),
         name='patients-medication-past-check-side-effect-n06'),
    path('patients/medication/past-check/side-effect_N07/', PastMedicationSideEffect_N07.as_view(),
         name='patients-medication-past-check-side-effect-n07'),
    path('patients/medication/past-check/side-effect_N08/', PastMedicationSideEffect_N08.as_view(),
         name='patients-medication-past-check-side-effect-n08'),
    path('patients/medication/past-check/side-effect_N09/', PastMedicationSideEffect_N09.as_view(),
         name='patients-medication-past-check-side-effect-n09'),
    path('patients/medication/past-check/side-effect_N10/', PastMedicationSideEffect_N10.as_view(),
         name='patients-medication-past-check-side-effect-n10'),
    path('patients/medication/past-check/side-effect_N11/', PastMedicationSideEffect_N11.as_view(),
         name='patients-medication-past-check-side-effect-n11'),
    path('patients/visit/start/', PatientVisitStart.as_view(), name='patient-visit-start'),
    path('patients/visit/date/set/', PatientVisitDateSet.as_view(), name='patient-visit-date-set'),
    path('patients/visit/noti/time/', PatientVisitNotiTimeBefore.as_view(), name='patient-visit-noti-time'),
    path('patients/visit/restart/', PatientVisitRestart.as_view(), name='patient-visit-restart'),
    path('patients/measurement/entrance/', PatientMeasurementEntrance.as_view(), name='patient-measurement-entrance'),
    path('patients/measurement/noti/time/question/', PatientMeasurementNotiTimeQuestion.as_view(),
         name='patient-measurement-noti-time-question'),
    path('patients/measurement/noti/time/set/', PatientMeasurementNotiSetTime.as_view(),
         name='patient-measurement-noti-set-time'),
    path('patients/measurement-result/create/', MeasurementResultCheck.as_view(), name='patient-measurement-create'),
    path('patients/measurement/check/', MeasurementResultCheckFromNotification.as_view(), name='patient-measurement-check'),
    path('patients/measurement/restart/', PatientMeasurementRestart.as_view(), name='patient-measurement-restart'),
    path('patients/measurement/noti/reset/', PatientMeasurementNotiReset.as_view(),
         name='patient-measurement-noti-reset'),
    path('patients/safeout/', PatientSafeOut.as_view(), name='patient-safeout'),
    path('patients/weight/', PatientWeight.as_view(), name='patient-weight'),
    path('patients/vision/', PatientVision.as_view(), name='patient-vision'),
    path('patients/code/print/', PatientCodePrint.as_view(), name='patient-code-print'),
    path('temp/patient/delete/', TempPatientDestroy.as_view(), name='temp-patient-destroy'),
    path('validate/patient/name/', ValidatePatientName.as_view(), name='validate-patient-name'),
    path('validate/patient/code/', ValidatePatientCode.as_view(), name='validate-patient-code'),
    path('validate/patient/nickname/', ValidatePatientNickname.as_view(), name='validate-patient-nickname'),
    path('validate/patient/phone/', ValidatePatientPhone.as_view(), name='validate-patient-phone'),
    path('validate/patient/password/', ValidatePatientPassword.as_view(), name='validate-patient-password'),
    path('validate/patient/weight/', ValidatePatientWeight.as_view(), name='validate-patient-weight'),
    path('validate/patient/vision/', ValidatePatientVision.as_view(), name='validate-patient-vision'),
    path('validate/hospital/code/', ValidateHospitalCode.as_view(), name='validate-hospital-code'),
    path('validate/time-before/', ValidateTimeBefore.as_view(), name='validate-time-before'),
    path('validate/measurement-result/oxygen-saturation/', ValidateMeasurementResultOxygenSaturation.as_view(),
         name='validate-measurement-result-oxygen-saturation'),
    path('general/response-always-ok/', ResponseAlwaysOK.as_view(),
         name='general-response-always-ok'),
    path('guardian/create/start/', GuardianCreateStart.as_view(), name = 'guardian-create-start'),
    path('guardian/create/', GuardianCreate.as_view(), name = 'guardian-create'),
    path('guardian/phone/', GuardianPhone.as_view(), name = 'guardian-phone'),
    path('guardian/check/medication', GuardianCheckPatientMedication.as_view(), name = 'guardian-check-patient-medication'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
