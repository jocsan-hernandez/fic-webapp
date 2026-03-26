from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, timezone
from usuarios.models import User
from depositos.models import Movimiento
from .services import calcularTasaCliente

def depositos(request):
    return render(request, "depositos.html", {})



def deposito_ajax(request):
    if request.method == "POST":
        identidad = request.POST.get("identidad")
        tipo = request.POST.get("tipo")
        monto = request.POST.get("monto")

        if not identidad or not monto or not tipo:
            return JsonResponse({"success": False, "message": "Todos los campos son requeridos."})

        if tipo not in ["capitalInicial", "interes", "retiro"]:
            return JsonResponse({"success": False, "message": "Tipo de depósito inválido."})

        cliente = User.objects(tipoUsuario="cliente", identidad=identidad).first()
        if not cliente:
            return JsonResponse({"success": False, "message": "Cliente no encontrado."})

        try:
            monto = float(monto)
            if monto <= 0:
                return JsonResponse({"success": False, "message": "Monto inválido."})
        except ValueError:
            return JsonResponse({"success": False, "message": "Monto inválido."})

        movimiento = Movimiento(
            user=cliente,
            monto=monto,
            tipo=tipo,
            descripcion=f"Depósito tipo {tipo} realizado vía web",
            fecha_operacion=datetime.now(timezone.utc).date()
        )
        movimiento.save()

        return JsonResponse({"success": True, "message": f"Depósito de {monto} ({tipo}) realizado para {cliente.nombreCompleto}."})

    return JsonResponse({"success": False, "message": "Método no permitido."})

def tasaClienteEndPoint(request, identidad, periodo):
    """
    Endpoint para consultar la tasa devengada de un cliente.
    Solo acepta método GET.
    Query params:
        identidad: str (requerido)
        periodo: str, uno de '1m', '3m', '6m', '1y' (requerido)
    """
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido, use GET"}, status=405)

    if not identidad or not periodo:
        return JsonResponse({"error": "Faltan parámetros 'identidad' o 'periodo'"}, status=400)

    try:
        resultado = calcularTasaCliente(identidad, periodo)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        # Error genérico
        return JsonResponse({"error": "Error interno del servidor"}, status=500)

    return JsonResponse(resultado)