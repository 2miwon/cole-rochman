from core.models import Patient


class RegisterNotifications:
    queryset = Patient.objects.all()

    class TYPE(Patient.NOTI_TYPE):
        pass

    class TIME_FIELDS(Patient.NOTI_TIME_FIELDS):
        pass

    def check_noti_flag(self, obj: Patient, type: TYPE) -> bool:
        """
        chack noti_flag of matching type is True or False

        :param obj: Patient
        :param type: TYPE Enum. MEDICATION, VISIT, MEASUREMENT
        :return: bool.
        """
        if type == self.TYPE.MEDICATION:
            return obj.is_medication_noti_sendable()
        elif type == self.TYPE.VISIT:
            return obj.is_visit_noti_sendable()
        elif type == self.TYPE.MEASUREMENT:
            return obj.is_measurement_noti_sendable()
        else:
            raise ValueError('TYPE has to be one of these: %s' % str([n for n in self.TYPE]))

    def filter_noti_target(self, type: TYPE):
        """
        find queryset that have True value in notification_flag of matching type.

        :param type: TYPE Enum. MEDICATION, VISIT, MEASUREMENT
        :return queryset
        """

        queryset = self.queryset
        if type == self.TYPE.MEDICATION:
            return queryset.filter(medication_manage_flag=True, medication_noti_flag=True)
        elif type == self.TYPE.VISIT:
            return queryset.filter(visit_manage_flag=True, visit_noti_flag=True)
        elif type == self.TYPE.MEASUREMENT:
            return queryset.filter(measurement_manage_flag=True, measurement_noti_flag=True)
        else:
            raise ValueError('TYPE has to be one of these: %s' % str([n for n in self.TYPE]))

    # def register_daily_notification(self, queryset, type: TYPE):
