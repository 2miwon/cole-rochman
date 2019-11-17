from django.db import models


class Hospital(models.Model):
    code = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '병원/기관'
        verbose_name_plural = '병원/기관'

    def __str__(self):
        return f'{self.name}({self.code})'
