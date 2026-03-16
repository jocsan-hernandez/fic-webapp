from django.urls import path
from .views import register, loginView, logoutView, forgottenPassword, verify_reset_code, restablecerPswd, viewProfile, updateProfile

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", loginView, name="login"),
    path("logout/", logoutView, name="logout"),
    path("forgottenPassword/", forgottenPassword, name="forgot"),
    path("verify-reset-code/", verify_reset_code, name="verify-reset-code"),
    path("resetPassword/", restablecerPswd, name="resetPassword"),
    path("viewProfile/", viewProfile, name="viewProfile"),
    path("updateProfile/", updateProfile, name="updateProfile")
]