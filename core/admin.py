from django.contrib import admin

from core.models import NotificationRecord, MeasurementResult, MedicationResult
from .models import Patient, Hospital


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    pass


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    pass


@admin.register(NotificationRecord)
class NotificationRecordAdmin(admin.ModelAdmin):
    pass


@admin.register(MeasurementResult)
class MeasurementResultAdmin(admin.ModelAdmin):
    pass


@admin.register(MedicationResult)
class MedicationResultAdmin(admin.ModelAdmin):
    pass
