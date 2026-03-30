from django.shortcuts import render, redirect
from mongoengine.errors import NotUniqueError
from django.http import JsonResponse
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm, JoinRequestForm
from .models import User, PasswordResetCode, Request
from .utils import generarCodigo
from django.conf import settings
from django.core.mail import get_connection, EmailMessage, EmailMultiAlternatives
import json
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from depositos.models import Movimiento
#Registro de usuarios
def register(request):
    mensaje_error=None
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
        return redirect("viewProfile")
    
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
                    if user.tipoUsuario=="admin":
                        return redirect("admin")
                    else:
                        return redirect("viewProfile")
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

#Vista de entrada de usuario
def viewProfile(request):
    userId= request.session.get("user_id")
    if not userId:
        return redirect("login")
    
    user= User.objects(id=userId).first()

    if not user:
        return redirect("login")
    
    cuenta_last4=None

    if user.cuentaBanco:
        try:
            cuenta= user.getCuentaBanco()
            cuenta_last4= cuenta[-4:]
        except:
            cuenta_last4 = None


    return render(request, "viewProfile.html", {"user":user, "cuenta_last4":cuenta_last4}) 

#Modificacion de usuario
def updateProfile(request):
    mensaje_exito = None
    userId = request.session.get("user_id")
    if not userId:
        return redirect("login")
    
    try:
        user = User.objects.get(id=userId)
    except User.DoesNotExist:
        return redirect("login")
    
    if request.method == "POST":
        form = UserUpdateForm(request.POST)
        if form.is_valid():
            user.nombreCompleto = form.cleaned_data["nombreCompleto"]
            user.correo = form.cleaned_data["correo"]
            user.telefono = form.cleaned_data["telefono"]
            user.nombreBanco = form.cleaned_data.get("nombreBanco", '')
            cuenta = form.cleaned_data.get("cuentaBanco", '')
            user.identidad = form.cleaned_data["identidad"]    
            if cuenta:
                user.setCuentaBanco(cuenta)

            user.save()
            mensaje_exito = "Perfil actualizado correctamente"

    else:
        datosIniciales = {
            'nombreCompleto': user.nombreCompleto,
            'identidad': user.identidad,
            'correo': user.correo,
            'telefono': user.telefono,
            'nombreBanco': user.nombreBanco,
            'cuentaBanco': user.getCuentaBanco() if user.cuentaBanco else ''
        }
        form = UserUpdateForm(initial=datosIniciales)

    return render(request, "updateProfile.html", {'form': form, "mensaje_exito": mensaje_exito})

def joinNow(request):
    mensaje_error=None
    if request.method == "POST":
        form = JoinRequestForm(request.POST)

        if form.is_valid():
            req = Request(
                nombreCompleto=form.cleaned_data["nombreCompleto"],
                telefono=form.cleaned_data["telefono"]
            )


            try:
                req.save()
                mensaje_error="Tu solicitud fue recibida, nuestro equipo se contactará contigo pronto."
            except:
                mensaje_error = "Error en el servidor, intenta de nuevo más tarde."

    else:
        form = JoinRequestForm()

    return render(request, "joinNow.html", {"form": form, "mensaje_error":mensaje_error})

def adminProfile(request):
    try:
        if request.session['user_tipo']!="admin":
            return redirect("login")
    except:
        return redirect("login")    
    #Traremos todas las solicitudes
    solicitudes = Request.objects()
    return render(request, "adminProfile.html", {"solicitudes":solicitudes})

#Endpoint para solicitudes
def obtenerSolicitudes(request):
    try:
        if request.session['user_tipo'] != "admin":
            return JsonResponse({"error": "No autorizado"}, status=403)
    except:
        return JsonResponse({"error": "No autenticado"}, status=401)

    solicitudes = Request.objects()

    data = []
    for s in solicitudes:
        data.append({
            "nombreCompleto": s.nombreCompleto,
            "telefono": s.telefono
        })

    return JsonResponse(data, safe=False)




def metricasAdmin(request):

    # Validación de sesión
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = User.objects(id=user_id).first()

    if not user or user.tipoUsuario != "admin":
        return redirect("login")

    # -----------------------------
    # QUERYSETS BASE
    # -----------------------------
    clientes_qs = User.objects(tipoUsuario="cliente")
    admins_qs = User.objects(tipoUsuario="admin")

    # IMPORTANTE: solo IDs (optimizado)
    clientes_ids = clientes_qs.scalar("id")

    # -----------------------------
    # MÉTRICAS GENERALES
    # -----------------------------
    total = User.objects.count()
    clientes = clientes_qs.count()
    admins = admins_qs.count()

    # -----------------------------
    # MÉTRICAS CLIENTES
    # -----------------------------
    con_cuenta = clientes_qs.filter(cuentaBanco__ne=None).count()
    sin_cuenta = clientes_qs.filter(cuentaBanco=None).count()

    # -----------------------------
    # ACTIVIDAD (correcto para Mongo)
    # -----------------------------
    activos = len(Movimiento.objects(
        user__in=clientes_ids
    ).distinct("user"))

    inactivos = clientes - activos

    # -----------------------------
    # COMPORTAMIENTO
    # -----------------------------
    depositaron = len(Movimiento.objects(
        tipo="capitalInicial",
        user__in=clientes_ids
    ).distinct("user"))

    retiraron = len(Movimiento.objects(
        tipo="retiro",
        user__in=clientes_ids
    ).distinct("user"))


    context = {
        "total": total,
        "clientes": clientes,
        "admins": admins,
        "con_cuenta": con_cuenta,
        "sin_cuenta": sin_cuenta,
        "activos": activos,
        "inactivos": inactivos,
        "depositaron": depositaron,
        "retiraron": retiraron,
    }

    return render(request, "metricasAdmin.html", context)