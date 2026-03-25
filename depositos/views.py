from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, timezone
from usuarios.models import User
from depositos.models import Movimiento

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