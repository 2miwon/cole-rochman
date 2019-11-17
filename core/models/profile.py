import datetime
from enum import Enum

from django.contrib.postgres.fields import JSONField
from django.db import models
from datetime import timedelta
from django.contrib.auth.models import User

from core.models.helper.helper import EnumField
from core.serializers import NotificationRecordSerializer



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=10)
    hospital = models.ForeignKey('Hospital', on_delete=models.SET_NULL, related_name='profiles', null=True)
