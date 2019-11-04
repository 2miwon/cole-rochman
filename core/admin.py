from django.contrib import admin
from .models import Patient, Hospital


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    pass


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    pass
