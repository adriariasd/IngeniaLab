"""Utilidades compartidas por los endpoints JSON."""
import json

from django.http import JsonResponse


def read_json(request):
    try:
        return json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return {}


def ok(**data):
    return JsonResponse({"ok": True, **data})


def fail(message, status=400, **data):
    return JsonResponse({"ok": False, "message": message, **data}, status=status)
