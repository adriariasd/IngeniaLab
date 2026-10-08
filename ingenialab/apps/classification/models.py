import uuid

from django.db import models

from apps.interviews.models import MasterRequirement, StudentAttempt


class StudentClassification(models.Model):
    """Clasificación RF/RNF confirmada por el estudiante (student_classifications, SDS §4.1)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(StudentAttempt, on_delete=models.CASCADE, related_name="classifications")
    master_requirement = models.ForeignKey(MasterRequirement, on_delete=models.CASCADE)
    selected_category = models.CharField(max_length=3, choices=MasterRequirement.TYPES)
    is_correct = models.BooleanField()
    times_changed = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_classifications"
        ordering = ["updated_at"]
        constraints = [
            # Evita duplicidad al reclasificar (SDS §4.1).
            models.UniqueConstraint(fields=["attempt", "master_requirement"], name="unique_classification_per_attempt"),
            models.CheckConstraint(condition=models.Q(selected_category__in=["RF", "RNF"]), name="classification_type_valid"),
        ]
