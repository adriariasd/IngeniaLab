from django.urls import path

from . import views

app_name = "progress"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("reportes/", views.report_summary, name="reports"),
    path("reportes/descargar/", views.report_download, name="report_download"),
]
