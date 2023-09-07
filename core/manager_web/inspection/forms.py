from dataclasses import field
from django.forms import ModelForm
from django import forms
from core.models.patient import Sputum_Inspection
from ..models import Post,Comment

class InspectionForm(ModelForm):
    class Meta:
        model = Sputum_Inspection
        # fields = '__all__'
        fields = ['insp_date','method','th', 'smear_result', 'culture_result']