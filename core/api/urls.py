from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns


from .views import PatientCreate, TestView

urlpatterns = [
    path('patients', PatientCreate.as_view(), name='patient-create'),
    path('test', TestView.as_view(), name='test')
]

urlpatterns = format_suffix_patterns(urlpatterns)