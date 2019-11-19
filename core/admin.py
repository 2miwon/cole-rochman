from django.contrib import admin

from .models import Patient, Hospital, MeasurementResult, MedicationResult
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'hospital', 'phone_number', 'kakao_user_id', 'nickname', 'daily_medication_count',
        'medication_noti_time_1', 'medication_noti_time_2', 'medication_noti_time_3', 'medication_noti_time_4',
        'medication_noti_time_5', 'next_visiting_date_time'
    )
    search_fields = (
        'patient__code',
        'patient__kakao_user_id',
    )
    list_filter = [
        'hospital', 'medication_manage_flag', 'measurement_manage_flag', 'visit_manage_flag',
        'medication_noti_flag', 'visit_notification_flag', 'measurement_noti_flag'
    ]


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    pass


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(MeasurementResult)
class MeasurementResult(admin.ModelAdmin):
    pass


@admin.register(MedicationResult)
class MeadicationResult(admin.ModelAdmin):
    pass
