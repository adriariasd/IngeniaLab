import uuid

from django.conf import settings
from django.db import models

DEFECT_TYPES = [
    ("ambiguity", "Ambigüedad"),
    ("incomplete", "Omisión / Incompletitud"),
    ("inconsistency", "Inconsistencia / Contradicción"),
    ("unverifiable", "No verificable"),
    ("redundancy", "Redundancia"),
    ("design", "Imposición de diseño"),
]
DEFECT_LABELS = dict(DEFECT_TYPES)


class InspectionExercise(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.title

    @property
    def defect_count(self):
        return self.fragments.exclude(defect_type="").count()


class InspectionFragment(models.Model):
    """Sección del artefacto precargado; `defect_type` vacío ⇒ fragmento correcto."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exercise = models.ForeignKey(InspectionExercise, on_delete=models.CASCADE, related_name="fragments")
    order = models.PositiveIntegerField()
    label = models.CharField(max_length=20)
    text = models.TextField()
    defect_type = models.CharField(max_length=20, choices=DEFECT_TYPES, blank=True)
    explanation = models.TextField()
    hint = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]


class InspectionAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inspections")
    exercise = models.ForeignKey(InspectionExercise, on_delete=models.PROTECT, related_name="attempts")
    started_at = models.DateTimeField(auto_now_add=True)
    concluded_at = models.DateTimeField(null=True, blank=True)
    hints_used = models.PositiveIntegerField(default=0)
    registrations = models.PositiveIntegerField(default=0)
    wrong_registrations = models.PositiveIntegerField(default=0)
    precision = models.FloatField(default=0.0)
    score = models.IntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]

    @property
    def is_concluded(self):
        return self.concluded_at is not None


class InspectionFinding(models.Model):
    attempt = models.ForeignKey(InspectionAttempt, on_delete=models.CASCADE, related_name="findings")
    fragment = models.ForeignKey(InspectionFragment, on_delete=models.CASCADE)
    selected_type = models.CharField(max_length=20, choices=DEFECT_TYPES)
    is_correct = models.BooleanField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fragment__order"]
        unique_together = ("attempt", "fragment")
