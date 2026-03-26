from datetime import datetime, timedelta, timezone
from .models import Movimiento
from usuarios.models import User

PERIODOS = {
    "1m": 30,
    "3m": 90,
    "6m": 180,
    "1y": 365
}

def calcularTasaCliente(identidad, periodo):
    if periodo not in PERIODOS:
        raise ValueError("Periodo inválido")

    dias_total = PERIODOS[periodo]

    fecha_fin = datetime.now(timezone.utc).date()
    fecha_inicio = fecha_fin - timedelta(days=dias_total)

    user = User.objects(identidad=identidad).first()
    if not user:
        return {"error": "Usuario no encontrado"}

    movimientos = Movimiento.objects(
        user=user,
        fecha_operacion__lte=fecha_fin
    ).order_by("fecha_operacion", "created_at")  # ordenar por created_at para consistencia

    if not movimientos:
        return {"error": "Sin movimientos"}

    capital = 0
    capital_al_inicio = 0
    eventos = []

    # Reconstruir capital histórico completo
    for mov in movimientos:
        fecha = mov.fecha_operacion

        # Solo afectar el capital con movimientos de tipo capitalInicial o retiro
        if mov.tipo == "capitalInicial":
            capital += mov.monto
        elif mov.tipo == "retiro":
            capital -= mov.monto

        # Guardar capital justo antes del inicio del período
        if fecha <= fecha_inicio:
            capital_al_inicio = capital

        # Guardar eventos SOLO para capital dentro del período
        if fecha >= fecha_inicio and mov.tipo in ["capitalInicial", "retiro"]:
            eventos.append({
                "fecha": fecha,
                "capital": capital
            })

    # Insertar capital al inicio del período solo si no hay un evento en fecha_inicio
    if not eventos or eventos[0]["fecha"] != fecha_inicio:
        eventos.insert(0, {
            "fecha": fecha_inicio,
            "capital": capital_al_inicio
        })

    # Capital promedio ponderado
    suma_ponderada = 0
    dias_acumulados = 0

    for i in range(len(eventos)):
        fecha_actual = eventos[i]["fecha"]
        capital_actual = eventos[i]["capital"]

        if i < len(eventos) - 1:
            fecha_siguiente = eventos[i + 1]["fecha"]
        else:
            fecha_siguiente = fecha_fin

        dias = max((fecha_siguiente - fecha_actual).days, 1)

        suma_ponderada += capital_actual * dias
        dias_acumulados += dias

    if dias_acumulados == 0:
        return {"error": "No se pudo calcular capital promedio"}

    capital_promedio = suma_ponderada / dias_acumulados

    if capital_promedio <= 0:
        return {"error": "Capital promedio inválido"}

    # Intereses del período (solo tipo "interes")
    intereses = Movimiento.objects(
        user=user,
        tipo="interes",
        fecha_operacion__gte=fecha_inicio,
        fecha_operacion__lte=fecha_fin
    ).sum("monto") or 0

    # Tasa del período solicitado
    tasa = intereses / capital_promedio

    return {
        "identidad": identidad,
        "periodo": periodo,
        "intereses_pagados": round(intereses, 2),
        "capital_promedio": round(capital_promedio, 2),
        "tasa": round(tasa, 4),
        "capital": round(capital,2)
    }