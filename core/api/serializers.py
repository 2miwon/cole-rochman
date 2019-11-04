from rest_framework.serializers import ModelSerializer

from core.models import Patient


class PatientCreateSerializer(ModelSerializer):
    class Meta:
        model = Patient
        exclude = ('created_at', 'updated_at')
        lookup_field = 'kakao_user_id'


class PatientUpdateSerializer(ModelSerializer):
    class Meta:
        model = Patient
        exclude = ('created_at', 'updated_at')
        lookup_field = 'kakao_user_id'
