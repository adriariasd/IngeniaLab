from django.conf import settings

from .services import level_for, total_points


def progress_summary(request):
    ctx = {"modules": settings.INGENIALAB_MODULES}
    if "progress" in ctx["modules"] and getattr(request, "user", None) and request.user.is_authenticated:
        points = total_points(request.user)
        ctx.update(nav_points=points, nav_level=level_for(points))
    return ctx
