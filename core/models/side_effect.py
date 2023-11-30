from django.db import models
from datetime import datetime


class SideEffect(models.Model):
    symptom_name = models.TextField()
    medication_result = models.ForeignKey(
        "MedicationResult",
        on_delete=models.SET_NULL,
        related_name="side_effects",
        blank=True,
        null=True,
    )
    intensity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
