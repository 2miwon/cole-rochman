from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from import_export.admin import ImportExportModelAdmin

from core.models import NotificationRecord
from .models import Patient, Hospital, MeasurementResult, MedicationResult
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile
from import_export.widgets import ForeignKeyWidget
from import_export import resources, fields


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
        'code', 'hospital', 'name', 'phone_number', 'kakao_user_id', 'nickname', 'daily_medication_count',
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
        'id', 'patient', 'date', 'medication_time_num', 'medication_time', 'get_status_display', 'status_info',
        'severity',
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
        'id', 'patient', 'medication_result', 'measurement_result', 'biz_message_type', 'noti_time_num', 'status',
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
