from django.conf import settings
from django.db import models


class UserBadge(models.Model):
    """Insignia formativa otorgada (sin carácter de calificación oficial)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badges")
    code = models.CharField(max_length=40)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "code")
        ordering = ["awarded_at"]


class ReportExport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports")
    report_id = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
