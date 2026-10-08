"""ModelingValidator (SCI-04): completitud y consistencia estructural de la plantilla (RF-04)."""
import re

INFINITIVE = re.compile(r"^\s*[a-záéíóúñ]+(ar|er|ir)(se)?\b", re.IGNORECASE)
REQUIRED_MESSAGE = "Debe ingresar al menos un actor principal y los pasos del flujo básico para generar el diagrama."


def _clean_list(values):
    if isinstance(values, str):
        values = values.splitlines()
    return [v.strip() for v in (values or []) if isinstance(v, str) and v.strip()]


def normalize(data: dict) -> dict:
    relations = []
    for r in data.get("relations") or []:
        target = (r.get("target") or "").strip()
        if target:
            relations.append({"type": "extend" if r.get("type") == "extend" else "include", "target": target})
    return {
        "name": (data.get("name") or "").strip(),
        "system_name": (data.get("system_name") or "").strip() or "Sistema",
        "primary_actors": _clean_list(data.get("primary_actors")),
        "secondary_actors": _clean_list(data.get("secondary_actors")),
        "preconditions": (data.get("preconditions") or "").strip(),
        "main_flow": _clean_list(data.get("main_flow")),
        "alternate_flows": _clean_list(data.get("alternate_flows")),
        "postconditions": (data.get("postconditions") or "").strip(),
        "relations": relations,
        "attempt_id": data.get("attempt_id") or "",
    }


def validate(spec: dict):
    """Devuelve (errores_por_campo, advertencias). Sin errores ⇒ la plantilla es válida."""
    errors, warnings = {}, []
    if not spec["name"]:
        errors["name"] = "Escribe el nombre del caso de uso."
    elif not INFINITIVE.match(spec["name"]):
        warnings.append("Buena práctica: nombra el caso de uso con un verbo en infinitivo (p. ej. «Registrar préstamo»).")
    if not spec["primary_actors"]:
        errors["primary_actors"] = "Agrega al menos un actor principal."
    if len(spec["main_flow"]) < 2:
        errors["main_flow"] = "El flujo principal debe tener al menos dos pasos (acción del actor y reacción del sistema)."
    if not spec["preconditions"]:
        errors["preconditions"] = "Indica las precondiciones (escribe «Ninguna» si no aplica)."
    if not spec["postconditions"]:
        errors["postconditions"] = "Indica las postcondiciones: el estado del sistema al terminar."

    lower = lambda xs: [x.lower() for x in xs]
    dup = set(lower(spec["primary_actors"])) & set(lower(spec["secondary_actors"]))
    if dup:
        errors["secondary_actors"] = f"Un actor no puede ser principal y secundario a la vez: {', '.join(sorted(dup))}."
    for field in ("primary_actors", "secondary_actors"):
        if len(set(lower(spec[field]))) != len(spec[field]) and field not in errors:
            errors[field] = "Hay actores repetidos en la lista."
    for r in spec["relations"]:
        if r["target"].lower() == spec["name"].lower():
            errors["relations"] = "Un caso de uso no puede incluirse o extenderse a sí mismo."
    if not spec["alternate_flows"]:
        warnings.append("Considera documentar al menos un flujo alterno o de excepción.")
    if spec["main_flow"] and spec["primary_actors"]:
        mentioned = any(a.lower() in " ".join(spec["main_flow"]).lower() for a in spec["primary_actors"])
        if not mentioned:
            warnings.append("Consistencia: el flujo principal no menciona a ningún actor principal.")
    return errors, warnings
