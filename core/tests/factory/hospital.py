import factory

from core.models import Hospital


class HospitalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Hospital

    code = 'A001'
    name = '서북병원'
