from rest_framework import serializers

from core.models import Patient, Hospital, MeasurementResult
from core.models.guardian import Guardian

class PatientCreateSerializer(serializers.ModelSerializer):
    hospital = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Hospital.objects.all()
    )

    class Meta:
        model = Patient
#        fields = ['code','hospital','kakao_user_id','nickname','phone_number','name','user','created_at','updated_at']
        exclude = ('created_at', 'updated_at')
        lookup_field = 'kakao_user_id'


class PatientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude = ('created_at', 'updated_at')
        lookup_field = 'kakao_user_id'


class MeasurementResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementResult
        exclude = ('created_at', 'updated_at')

class GuardianCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = '__all__'

