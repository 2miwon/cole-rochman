from enum import Enum

from core.models import Patient
from core.models import Patient

Patient.objects.filter(medication_noti_flag=True).all()


class RegisterNotifications:
    queryset = Patient.objects.all()

    class Type(Patient.NotiType):
        pass

    class TimeFields(Patient.NotiTimeFields):
        pass

    def check_noti_flag(self, obj: Patient, type: Type) -> bool:
        """
        chack noti_flag of matching type is True or False

        :param obj: Patient
        :param type: Type Enum. MEDICATION, VISIT, MEASUREMENT
        :return: bool.
        """
        if type == self.Type.MEDICATION:
            return obj.is_medication_noti_sendable()
        elif type == self.Type.VISIT:
            return obj.is_visit_noti_sendable()
        elif type == self.Type.MEASUREMENT:
            return obj.is_measurement_noti_sendable()
        else:
            raise ValueError('Type has to be one of these: %s' % str([n for n in self.Type]))

    def filter_noti_target(self, type: Type):
        """
        find queryset that have True value in notification_flag of matching type.

        :param type: Type Enum. MEDICATION, VISIT, MEASUREMENT
        :return queryset
        """

        queryset = self.queryset
        if type == self.Type.MEDICATION:
            return queryset.filter(medication_manage_flag=True, medication_noti_flag=True)
        elif type == self.Type.VISIT:
            return queryset.filter(visit_manage_flag=True, visit_noti_flag=True)
        elif type == self.Type.MEASUREMENT:
            return queryset.filter(measurement_manage_flag=True, measurement_noti_flag=True)
        else:
            raise ValueError('Type has to be one of these: %s' % str([n for n in self.Type]))

    # def register_daily_notification(self, queryset, type: Type):
    #     if type == self.Type.MEDICATION:
    #         queryset.
    #     elif type == self.Type.VISIT:
    #         # return queryset.filter(visit_manage_flag=True, visit_noti_flag=True)
    #     elif type == self.Type.MEASUREMENT:
    #         # return queryset.filter(measurement_manage_flag=True, measurement_noti_flag=True)
    #     else
    #         raise ValueError('Type has to be one of these: %s' % str([n for n in self.Type]))

