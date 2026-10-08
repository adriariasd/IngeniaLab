"""SessionGuard (SCI-01): las peticiones a /api/ sin sesión activa reciben 401 JSON.

Así el cliente JS puede conservar el estado en pantalla y pedir reautenticación (RF-12)
en lugar de recibir una redirección HTML.
"""
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect


class ApiSessionGuardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "/api/" in request.path and not request.user.is_authenticated:
            return JsonResponse(
                {"ok": False, "error": "session_expired",
                 "message": "Tu sesión expiró. Inicia sesión nuevamente; tu trabajo guardado se conserva."},
                status=401,
            )
        return self.get_response(request)


# Prefijo de URL → módulo que lo atiende. "/" exacto es el tablero (módulo progress).
MODULE_PREFIXES = [
    ("/clasificacion/", "classification"),
    ("/modelado/", "modeling"),
    ("/inspeccion/", "inspection"),
    ("/reportes/", "reports"),
]


class ModuleGateMiddleware:
    """Bloquea los módulos deshabilitados en settings.INGENIALAB_MODULES y redirige a la entrevista."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        enabled = settings.INGENIALAB_MODULES
        path = request.path
        module = "progress" if path == "/" else next((m for p, m in MODULE_PREFIXES if path.startswith(p)), None)
        if module and module not in enabled:
            if "/api/" in path:
                return JsonResponse({"ok": False, "message": "Este módulo no está disponible."}, status=404)
            return redirect("interviews:scenarios")
        return self.get_response(request)
