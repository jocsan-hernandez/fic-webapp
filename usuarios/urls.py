from django.urls import path
from .views import *
urlpatterns = [
    path("register/", register, name="register"),
    path("login/", loginView, name="login"),
    path("logout/", logoutView, name="logout"),
    path("forgottenPassword/", forgottenPassword, name="forgot"),
    path("verify-reset-code/", verify_reset_code, name="verify-reset-code"),
    path("resetPassword/", restablecerPswd, name="resetPassword"),
    path("viewProfile/", viewProfile, name="viewProfile"),
    path("updateProfile/", updateProfile, name="updateProfile"),
    path('joinNow/', joinNow, name='joinNow'),
    path('admin/', adminProfile, name='admin'),
    path('obtenerSolicitudes', obtenerSolicitudes, name="obtenerSolicitudes"),
    path('metricasAdmin/', metricasAdmin, name='metricasAdmin'),
    path("metricasMovimientos/", metricasMovimientos, name="metricasMovimientos"),
    path("clientesPorDepartamento/", clientesPorDepartamento, name="clientesPorDepartamento"),
    path("delete/<str:id>/", deleteRequest, name="deleteRequest"),
    path("cambioAdmin/", cambioAdmin, name="cambioAdmin")
]