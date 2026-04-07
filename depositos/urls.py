from django.urls import path
from .views import *
urlpatterns = [
    path("depositos/", depositos, name="depositos"),
    path("ajax/", deposito_ajax, name="depositosAjax"),
    path("calculoIntereses/<str:periodo>/", tasaClienteEndPoint, name="tasaClienteEndPoint"),
    path("listarMovimientos/", listarMovimientos, name="listarMovimientos"),
    path("metricas/", metricas, name="metricas"),
]