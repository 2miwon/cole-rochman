from rest_framework.serializers import ModelSerializer

from core.models import Patient, Test


class PatientSerializer(ModelSerializer):
    class Meta:
        model = Patient
        exclude = ('created_at', 'updated_at')


class TestSerializer(ModelSerializer):
    class Meta:
        model = Test
        exclude = ('created_at', )