from rest_framework.serializers import ModelSerializer

from core.models import NotificationRecord, MedicationResult, MeasurementResult


class NotificationRecordSerializer(ModelSerializer):
    class Meta:
        model = NotificationRecord
        exclude = ('created_at', 'updated_at')


class MedicationResultSerializer(ModelSerializer):
    class Meta:
        model = MedicationResult
        exclude = ('created_at', 'updated_at')


class MeasurementResultSerializer(ModelSerializer):
    class Meta:
        model = MeasurementResult
        exclude = ('created_at', 'updated_at')
