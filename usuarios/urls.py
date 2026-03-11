from django.urls import path
from .views import register, loginView, logoutView

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", loginView, name="login"),
    path("logout/", logoutView, name="logout"),
]