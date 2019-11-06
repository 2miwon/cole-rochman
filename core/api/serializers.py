from rest_framework import serializers


from core.models import Patient, Hospital,MeasurementResult


class PatientCreateSerializer(serializers.ModelSerializer):
    hospital = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Hospital.objects.all()
    )

    class Meta:
        model = Patient
        exclude = ('created_at', 'updated_at')
        lookup_field = 'kakao_user_id'


class PatientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude = ('created_at', 'updated_at')
        lookup_field = 'kakao_user_id'

