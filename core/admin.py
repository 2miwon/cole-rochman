from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from import_export.admin import ImportExportModelAdmin

from core.models import NotificationRecord
from .models import Patient, Hospital, MeasurementResult, MedicationResult,Certificaion
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile
from import_export.widgets import ForeignKeyWidget
from import_export import resources, fields
from core.models.patient import Pcr_Inspection, Sputum_Inspection
from core.models.guardian import Guardian
from core.models.community import Post,Comment


class PatientResource(resources.ModelResource):
    hospital = fields.Field(
        column_name='hospital',
        attribute='hospital',
        widget=ForeignKeyWidget(Hospital, 'code'))
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(User, 'username'))

    class Meta:
        model = Patient

        fields = ('id', 'code', 'hospital', 'phone_number', 'name', 'user')


@admin.register(Patient)
class PatientAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = PatientResource

    user_can_access_owned_objects_only = True
  
    list_display = (
        'code', 'hospital', 'name', 'gender', 'birth', 'phone_number', 'display_dashboard', 'nickname', 'safeout', 'daily_medication_count',
        'medication_noti_time_1', 'medication_noti_time_2', 'medication_noti_time_3', 'medication_noti_time_4',
        'medication_noti_time_5', 'next_visiting_date_time',
        'weight', 'vision_left', 'vision_right'
    )
    search_fields = (
        'patient__code',
        'patient__kakao_user_id',
        'name',
        'phone_number'
    )
    list_filter = [
        'hospital', 'medication_manage_flag', 'visit_manage_flag',
        'medication_noti_flag', 'visit_notification_flag',
        'display_dashboard',
        'safeout',
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
class MeasurementResultAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'patient', 'date', 'measurement_time_num', 'oxygen_saturation', 'measured_at'
    ]
    search_fields = [
        'patient__name'
    ]

    actions = ['make_status_pending', 'make_status_canceled']

    def make_status_pending(self, request, queryset):
        queryset.update(status=NotificationRecord.STATUS.PENDING.value)

    def make_status_canceled(self, request, queryset):
        queryset.update(status=NotificationRecord.STATUS.CANCELED.value)

    make_status_pending.short_description = "Mark selected as PENDING"
    make_status_canceled.short_description = "Mark selected as CANCELED"


@admin.register(MedicationResult)
class MedicationResultAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    list_display = [
        'id', 'patient', 'date', 'medication_time_num', 'medication_time', 'get_status_display', 'symptom_name',
        'symptom_severity1', 'symptom_severity2', 'symptom_severity3',
        'notified_at', 'checked_at'
    ]
    search_fields = [
        'patient__name'
    ]

    actions = ['make_status_pending', 'make_status_canceled']

    def get_status_display(self, obj):
        """STATUS"""
        try:
            return obj.status.split('.')[1]
        except IndexError:
            return obj.status

    def make_status_pending(self, request, queryset):
        queryset.update(status=NotificationRecord.STATUS.PENDING.value)

    def make_status_canceled(self, request, queryset):
        queryset.update(status=NotificationRecord.STATUS.CANCELED.value)

    get_status_display.short_description = 'STATUS'
    make_status_pending.short_description = "Mark selected as PENDING"
    make_status_canceled.short_description = "Mark selected as CANCELED"


@admin.register(NotificationRecord)
class NotificationRecordAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'patient', 'medication_result', 'noti_time_num', 'status',
        'recipient_number', 'tries_left', 'send_at', 'delivered_at', 'status_updated_at', 'created_at', 'updated_at'
    ]
    search_fields = [
        'patient__name', 'patient__code'
    ]
    actions = ['make_status_pending', 'make_status_canceled']

    def make_status_pending(self, request, queryset):
        queryset.update(status=NotificationRecord.STATUS.PENDING.value)

    def make_status_canceled(self, request, queryset):
        queryset.update(status=NotificationRecord.STATUS.CANCELED.value)

    make_status_pending.short_description = "Mark selected as PENDING"
    make_status_canceled.short_description = "Mark selected as CANCELED"


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    pass

#@admin.register(Post)
#class PostAdmin(admin.ModelAdmin):
#    pass

#@admin.register(Comment)
#class CommentAdmin(admin.ModelAdmin):
#    pass


@admin.register(Sputum_Inspection)
class SputumAdmin(admin.ModelAdmin):
    list_display = ['patient_set', 'insp_date', 'method', 'smear_result', 'culture_result']
    search_fields = ['patient_set__code', 'patient_set__nickname']

@admin.register(Pcr_Inspection)
class PcrAdmin(admin.ModelAdmin):
    list_display = ['patient_set', 'insp_date', 'method', 'pcr_result']
    search_fields = ['patient_set__code','patient_set__nickname']


#@admin.register(Certificaion)
#class Certificationadmin(admin.ModelAdmin):
#    pass

