import uuid

from django.conf import settings
from django.db import models

from apps.interviews.models import StudentAttempt


class UseCaseSpecification(models.Model):
    """Caso de uso estructurado por el estudiante (usecase_specifications, SDS §4.1)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="use_cases")
    attempt = models.ForeignKey(StudentAttempt, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="use_cases", help_text="Entrevista que sirve de guía")
    name = models.CharField(max_length=200)
    system_name = models.CharField(max_length=200, default="Sistema")
    # {"primary": [...], "secondary": [...]}
    actors = models.JSONField()
    preconditions = models.TextField()
    main_flow = models.JSONField()  # ["paso 1", "paso 2", ...]
    alternate_flows = models.JSONField(default=list)  # ["FA-1 ...", ...]
    postconditions = models.TextField()
    # [{"type": "include"|"extend", "target": "nombre CU"}]
    relations = models.JSONField(default=list)
    plantuml_code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "usecase_specifications"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name

    def as_form_data(self):
        return {
            "name": self.name,
            "system_name": self.system_name,
            "primary_actors": self.actors.get("primary", []),
            "secondary_actors": self.actors.get("secondary", []),
            "preconditions": self.preconditions,
            "main_flow": self.main_flow,
            "alternate_flows": self.alternate_flows,
            "postconditions": self.postconditions,
            "relations": self.relations,
            "attempt_id": str(self.attempt_id) if self.attempt_id else "",
        }


class GeneratedDiagram(models.Model):
    """Diagrama renderizado asociado 1:1 a la especificación."""

    use_case = models.OneToOneField(UseCaseSpecification, on_delete=models.CASCADE, related_name="diagram")
    code_hash = models.CharField(max_length=64)
    svg = models.TextField()
    engine = models.CharField(max_length=20)
    generated_at = models.DateTimeField(auto_now=True)
