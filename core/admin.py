from django.contrib import admin
from .models import Patient, Hospital,MeasurementResult,MedicationResult
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    pass


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    pass

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(MeasurementResult)
class MeasurementResult(admin.ModelAdmin):
    pass

@admin.register(MedicationResult)
class MeadicationResult(admin.ModelAdmin):
    pass