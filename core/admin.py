from django.contrib import admin
from .models import Patient, Test


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    pass


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    pass
