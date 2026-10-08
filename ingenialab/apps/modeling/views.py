from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.api import fail, ok, read_json
from apps.interviews.models import StudentAttempt
from apps.progress.services import evaluate_badges
from integrations.plantuml import service as plantuml
from integrations.plantuml.builder import build_usecase_diagram

from . import validators
from .models import GeneratedDiagram, UseCaseSpecification


def _finished_attempts(user):
    return user.attempts.filter(status=StudentAttempt.CLASSIFYING).select_related("version")


@login_required
def usecase_list(request):
    return render(request, "modeling/list.html", {
        "use_cases": request.user.use_cases.select_related("attempt__version"),
        "can_model": _finished_attempts(request.user).exists(),
    })


@login_required
def editor(request, uc_id=None):
    attempts = _finished_attempts(request.user)
    if not attempts.exists():
        # Precondición CU-02: al menos una entrevista completada.
        messages.warning(request, "Para modelar casos de uso primero completa al menos una entrevista en el módulo de Elicitación.")
        return redirect("modeling:list")
    uc = get_object_or_404(UseCaseSpecification, id=uc_id, user=request.user) if uc_id else None
    guide = []
    for a in attempts:
        guide.append({
            "id": str(a.id),
            "label": f"{a.version.title} ({a.started_at:%d/%m/%Y})",
            "system": a.version.title,
            "requirements": [
                {"statement": c.master_requirement.statement_text, "category": c.selected_category}
                for c in a.classifications.select_related("master_requirement")
            ],
        })
    return render(request, "modeling/editor.html", {
        "uc": uc,
        "form_data": uc.as_form_data() if uc else None,
        "svg": uc.diagram.svg if uc and hasattr(uc, "diagram") else "",
        "guide": guide,
    })


def _validate_and_render(data):
    spec = validators.normalize(data)
    errors, warnings = validators.validate(spec)
    if errors:
        return spec, None, None, errors, warnings
    code = build_usecase_diagram(spec)
    return spec, code, plantuml.render(code), errors, warnings


@require_POST
def api_generate(request):
    spec, code, result, errors, warnings = _validate_and_render(read_json(request))
    if errors:
        return fail(validators.REQUIRED_MESSAGE, errors=errors, warnings=warnings)
    return ok(plantuml_code=code, svg=result.svg, engine=result.engine, cached=result.cached, warnings=warnings)


@require_POST
@transaction.atomic
def api_save(request):
    data = read_json(request)
    spec, code, result, errors, warnings = _validate_and_render(data)
    if errors:
        return fail(validators.REQUIRED_MESSAGE, errors=errors, warnings=warnings)
    attempt = None
    if spec["attempt_id"]:
        attempt = _finished_attempts(request.user).filter(id=spec["attempt_id"]).first()
    fields = {
        "attempt": attempt,
        "name": spec["name"],
        "system_name": spec["system_name"],
        "actors": {"primary": spec["primary_actors"], "secondary": spec["secondary_actors"]},
        "preconditions": spec["preconditions"],
        "main_flow": spec["main_flow"],
        "alternate_flows": spec["alternate_flows"],
        "postconditions": spec["postconditions"],
        "relations": spec["relations"],
        "plantuml_code": code,
    }
    uc_id = data.get("id")
    if uc_id:
        # Actualización sin duplicar registros (CU-02 FA-1).
        uc = get_object_or_404(UseCaseSpecification, id=uc_id, user=request.user)
        for k, v in fields.items():
            setattr(uc, k, v)
        uc.save()
    else:
        uc = UseCaseSpecification.objects.create(user=request.user, **fields)
    GeneratedDiagram.objects.update_or_create(
        use_case=uc, defaults={"code_hash": result.code_hash, "svg": result.svg, "engine": result.engine},
    )
    return ok(id=str(uc.id), plantuml_code=code, svg=result.svg, engine=result.engine, warnings=warnings,
              message="Especificación guardada correctamente en tu cuenta.", badges=evaluate_badges(request.user))


@login_required
@require_POST
def delete(request, uc_id):
    uc = get_object_or_404(UseCaseSpecification, id=uc_id, user=request.user)
    uc.delete()
    messages.success(request, "Caso de uso eliminado.")
    return redirect("modeling:list")
