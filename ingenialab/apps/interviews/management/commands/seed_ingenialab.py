"""Carga idempotente de escenarios (data/interviews.json) e inspecciones (data/inspections.json)."""
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.inspection.models import InspectionExercise, InspectionFragment
from apps.interviews.models import InterviewQuestion, MasterRequirement, ScenarioVersion


class Command(BaseCommand):
    help = "Carga o actualiza los escenarios y ejercicios de inspección de IngeniaLab."

    def add_arguments(self, parser):
        parser.add_argument("--interviews", default=str(settings.BASE_DIR / "data" / "interviews.json"))
        parser.add_argument("--inspections", default=str(settings.BASE_DIR / "data" / "inspections.json"))

    @transaction.atomic
    def handle(self, *args, **opts):
        with open(opts["interviews"], encoding="utf-8") as fh:
            scenarios = json.load(fh)["scenarios"]
        with open(opts["inspections"], encoding="utf-8") as fh:
            inspections = json.load(fh)["inspections"]

        for sc in scenarios:
            version, created = ScenarioVersion.objects.update_or_create(
                scenario_code=sc["code"], version_number=sc["version"],
                defaults={"title": sc["title"], "summary": sc["summary"], "client_name": sc["client_name"],
                          "client_role": sc["client_role"], "client_greeting": sc["greeting"], "is_active": True},
            )
            if not created and version.attempts.exists():
                # Una versión con prácticas registradas es inmutable: publica una nueva versión en el JSON.
                self.stdout.write(self.style.WARNING(f"{version} ya tiene prácticas; se conserva sin cambios."))
                continue
            version.questions.all().delete()
            for round_number, rnd in enumerate(sc["rounds"], 1):
                qualities = sorted(o["quality"] for o in rnd["options"])
                if qualities != ["high", "low", "medium"]:
                    raise ValueError(f"{sc['code']} ronda {round_number}: se requiere una opción high, medium y low")
                for order, opt in enumerate(rnd["options"]):
                    question = InterviewQuestion.objects.create(
                        version=version, round_number=round_number, topic=rnd["topic"], text=opt["text"],
                        quality=opt["quality"], rationale=opt["rationale"], order=order,
                        answer_segments=[{"text": s["text"], "req": s["req"]["key"] if "req" in s else None}
                                         for s in opt["answer"]],
                    )
                    for s in opt["answer"]:
                        if "req" in s:
                            r = s["req"]
                            MasterRequirement.objects.create(
                                version=version, question=question, key=r["key"], statement_text=s["text"],
                                expected_type=r["type"], feedback_explanation=r["feedback"], hint=r.get("hint", ""),
                            )
            # Solo la versión recién cargada queda disponible para nuevas prácticas.
            ScenarioVersion.objects.filter(scenario_code=sc["code"]).exclude(id=version.id).update(is_active=False)
            self.stdout.write(self.style.SUCCESS(f"Escenario {version}: {version.requirements.count()} requisitos"))

        for ex in inspections:
            exercise, created = InspectionExercise.objects.update_or_create(
                code=ex["code"], defaults={"title": ex["title"], "description": ex["description"], "is_active": True},
            )
            if not created and exercise.attempts.exists():
                self.stdout.write(self.style.WARNING(f"{exercise.code} ya tiene prácticas; se conserva sin cambios."))
                continue
            exercise.fragments.all().delete()
            for order, fr in enumerate(ex["fragments"]):
                InspectionFragment.objects.create(
                    exercise=exercise, order=order, label=fr["label"], text=fr["text"],
                    defect_type=fr["defect"], explanation=fr["explanation"], hint=fr.get("hint", ""),
                )
            self.stdout.write(self.style.SUCCESS(f"Inspección {exercise.code}: {exercise.defect_count} defectos"))
