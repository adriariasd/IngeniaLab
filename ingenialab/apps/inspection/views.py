from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.api import fail, ok, read_json
from apps.progress.services import evaluate_badges

from . import services
from .models import DEFECT_LABELS, DEFECT_TYPES, InspectionAttempt, InspectionExercise


def _own(request, attempt_id):
    return get_object_or_404(InspectionAttempt, id=attempt_id, user=request.user)


@login_required
def exercise_list(request):
    return render(request, "inspection/list.html", {
        "exercises": InspectionExercise.objects.filter(is_active=True),
        "attempts": request.user.inspections.select_related("exercise"),
    })


@login_required
@require_POST
def start(request, exercise_id):
    exercise = get_object_or_404(InspectionExercise, id=exercise_id, is_active=True)
    attempt = InspectionAttempt.objects.create(user=request.user, exercise=exercise)
    return redirect("inspection:inspect", attempt_id=attempt.id)


@login_required
def inspect(request, attempt_id):
    attempt = _own(request, attempt_id)
    findings = {f.fragment_id: f for f in attempt.findings.all()}
    fragments = [
        {"f": fr, "finding": findings.get(fr.id),
         "label": DEFECT_LABELS.get(findings[fr.id].selected_type) if fr.id in findings else ""}
        for fr in attempt.exercise.fragments.all()
    ]
    return render(request, "inspection/inspect.html", {
        "attempt": attempt,
        "fragments": fragments,
        "defect_types": DEFECT_TYPES,
        "summary": services.summary(attempt),
    })


@require_POST
def api_finding(request, attempt_id):
    data = read_json(request)
    try:
        result = services.register_finding(_own(request, attempt_id), data.get("fragment_id"), data.get("defect_type"))
    except services.AuditError as e:
        return fail(str(e))
    return ok(**result)


@require_POST
def api_hint(request, attempt_id):
    try:
        return ok(**services.request_hint(_own(request, attempt_id)))
    except services.AuditError as e:
        return fail(str(e))


@require_POST
def api_conclude(request, attempt_id):
    try:
        result = services.conclude(_own(request, attempt_id))
    except services.AuditError as e:
        return fail(str(e))
    return ok(summary=result, badges=evaluate_badges(request.user))
