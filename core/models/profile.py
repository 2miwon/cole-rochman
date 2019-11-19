from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=10)
    hospital = models.ForeignKey('Hospital', on_delete=models.SET_NULL, related_name='profiles', null=True)
