from django.shortcuts import render, redirect
from mongoengine.errors import NotUniqueError
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm, UserLoginForm
from .models import User

#Registro de usuarios
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = User(
                nombreCompleto=form.cleaned_data["nombreCompleto"],
                identidad=form.cleaned_data["identidad"],
                telefono=form.cleaned_data["telefono"],
                correo=form.cleaned_data["correo"],
                nombreBanco=form.cleaned_data["nombreBanco"],
                tipoUsuario=form.cleaned_data["tipoUsuario"],
            )

            cuenta = form.cleaned_data.get("cuentaBanco")
            if cuenta:
                user.setCuentaBanco(cuenta)

            user.setPassword(form.cleaned_data["password"])

            try:
                user.save()
                return redirect("/") 
            except NotUniqueError:
                mensaje_error = "El correo o la identidad ya existen."

    else:
        form = UserRegisterForm()

    return render(request, "register.html", {"form": form, "mensaje_error":mensaje_error})

#Login de usuarios
def loginView(request):
    mensaje_error = None
    if request.session.get("user_id"):
        return redirect("index")
    
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data["correo"]
            password = form.cleaned_data["password"]

            try:
                user = User.objects.get(correo=correo)
                if user.checkPassword(password):
                    # Guardamos información mínima en sesión
                    request.session['user_id'] = str(user.id)
                    request.session['user_name'] = user.nombreCompleto
                    request.session['user_tipo'] = user.tipoUsuario

                    # Tiempo de expiración de la sesión (opcional, ya lo definiste en settings)
                    request.session.set_expiry(60 * 60 * 2)  # 2 horas

                    return redirect("index")
                else:
                    mensaje_error = "Correo o contraseña incorrectos"
            except User.DoesNotExist:
                mensaje_error = "Correo o contraseña incorrectos"
    else:
        form = UserLoginForm()

    return render(request, "login.html", {"form": form, "mensaje_error": mensaje_error})

#Vista de logout
def logoutView(request):
    # Limpia toda la sesión
    request.session.flush()
    # Redirige al inicio o login
    return redirect("index")