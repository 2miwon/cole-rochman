from operator import mod
from django.db import models
from django.contrib.auth.models import User

class Certificaion(models.Model):
    number = models.IntegerField(null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
