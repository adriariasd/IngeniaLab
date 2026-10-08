from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cuentas/", include("apps.accounts.urls")),
    path("elicitacion/", include("apps.interviews.urls")),
    path("clasificacion/", include("apps.classification.urls")),
    path("modelado/", include("apps.modeling.urls")),
    path("inspeccion/", include("apps.inspection.urls")),
    path("", include("apps.progress.urls")),
]
