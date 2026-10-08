from django.urls import path

from . import views

app_name = "classification"

urlpatterns = [
    path("intento/<uuid:attempt_id>/", views.classify, name="classify"),
    path("api/intento/<uuid:attempt_id>/clasificar/", views.api_classify, name="api_classify"),
    path("api/intento/<uuid:attempt_id>/pista/", views.api_hint, name="api_hint"),
]
