from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns


from .views import PatientCreate

urlpatterns = [
    path('patients', PatientCreate.as_view(), name='patient-create'),
]

urlpatterns = format_suffix_patterns(urlpatterns)