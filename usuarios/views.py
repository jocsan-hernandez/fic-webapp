from django.shortcuts import render, redirect
from mongoengine.errors import NotUniqueError
from django.http import JsonResponse
from .forms import UserRegisterForm, UserLoginForm
from .models import User, PasswordResetCode
from .utils import generarCodigo
from django.conf import settings
from django.core.mail import get_connection, EmailMessage, EmailMultiAlternatives
import json
from django.contrib.auth.hashers import check_password
from django.contrib import messages

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


def forgottenPassword(request):
    if request.method == "POST":
        correo = request.POST.get("correo", "").strip()
        user = User.objects(correo=correo).first()
        if user:
            # Borrar códigos previos
            PasswordResetCode.objects(correo=correo).delete()

            # Generar código
            codigo, codigoHash = generarCodigo()
            reset = PasswordResetCode(correo=correo, codigo=codigoHash)
            reset.save()

            #Guardamos en sesión
            request.session["reset_email"] = correo

            # Conexión SMTP con local_hostname válido
            
            connection = get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS,
                fail_silently=False,
                local_hostname="uth.hn"  # <- dominio válido
            )

            # Crear y enviar correo
            html_content = f"""
                                <div style="font-family: Arial, sans-serif; background-color:#f4f6f8; padding:30px;">
                                    
                                    <div style="max-width:500px; margin:auto; background:white; padding:30px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                                        
                                        <h2 style="text-align:center; color:#333;">Recuperación de contraseña</h2>
                                        
                                        <p style="font-size:15px; color:#555;">
                                        Hemos recibido una solicitud para recuperar tu contraseña.
                                        Utiliza el siguiente código para continuar:
                                        </p>

                                        <div style="text-align:center; margin:30px 0;">
                                            <span style="
                                                font-size:36px;
                                                letter-spacing:6px;
                                                font-weight:bold;
                                                color:#2c3e50;
                                                background:#eef2f7;
                                                padding:12px 25px;
                                                border-radius:6px;
                                                display:inline-block;
                                            ">
                                                {codigo}
                                            </span>
                                        </div>

                                        <p style="font-size:14px; color:#666;">
                                        Si no solicitaste este código, puedes ignorar este correo.
                                        </p>

                                        <hr style="margin:25px 0; border:none; border-top:1px solid #eee;">

                                        <p style="font-size:14px; color:#555;">
                                        Saludos desde el <strong>Grupo FIC</strong>.
                                        </p>

                                        <p style="font-size:12px; color:#999;">
                                        Este es un mensaje automático, por favor no respondas a este correo.
                                        </p>

                                    </div>

                                </div>
                                """

            email = EmailMultiAlternatives(
                                    subject="Recuperación de contraseña",
                                    body="Tu código de recuperación es: " + codigo,
                                    from_email=settings.EMAIL_HOST_USER,
                                    to=[correo],
                                    connection=connection
                                )

            email.attach_alternative(html_content, "text/html")
            email.send()

            return JsonResponse({"exists": True})
        return JsonResponse({"exists": False})
    return render(request, "forgottenPassword.html", {})

def verify_reset_code(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"valid": False})

        codigo_ingresado = data.get("codigo")
        correo = request.session.get("reset_email")

        if not correo or not codigo_ingresado:
            return JsonResponse({"valid": False})

        # Buscar el código guardado en Mongo
        reset = PasswordResetCode.objects(correo=correo).first()

        if reset and check_password(codigo_ingresado, reset.codigo):
            # Código correcto
            reset.delete()  # eliminar para que no se pueda reutilizar
            request.session["reset_verified"] = True
            return JsonResponse({"valid": True})
        else:
            return JsonResponse({"valid": False})

    return JsonResponse({"valid": False})


def restablecerPswd(request):
    mensaje_error = None

    # Verificamos que el código haya sido validado
    if not request.session.get("reset_verified") or not request.session.get("reset_email"):
        return redirect("login")  
    correo = request.session.get("reset_email")

    if request.method == "POST":
        pswd = request.POST.get("pswd", "").strip()
        pswd_confirmar = request.POST.get("pswdConfirmar", "").strip()

        if pswd != pswd_confirmar:
            mensaje_error = "Las contraseñas no coinciden"
        else:
            user = User.objects(correo=correo).first()
            if user:
                user.setPassword(pswd) 
                user.save()

                # Limpiamos la sesión de reset
                request.session.pop("reset_verified", None)
                request.session.pop("reset_email", None)

                messages.success(request, "Contraseña actualizada correctamente. Ya podés iniciar sesión.")
                return redirect("login")

            else:
                mensaje_error = "Usuario no encontrado"

    return render(request, "resetPassword.html", {"mensaje_error": mensaje_error})