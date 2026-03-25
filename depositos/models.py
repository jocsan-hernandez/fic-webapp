from mongoengine import Document, ReferenceField, FloatField, StringField, DateField, DateTimeField
from datetime import datetime, timezone
from usuarios.models import User

class Movimiento(Document):
    user = ReferenceField(User, required=True)
    monto = FloatField(required=True)
    tipo = StringField(
        choices=["capitalInicial", "interes", "retiro"],
        required=True
    )
    descripcion = StringField()

    fecha_operacion = DateField(required=True) 
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc)) 

    meta = {
        "collection": "movimientos",
        "ordering": ["-fecha_operacion", "-created_at"],
        "indexes": [
            "user",
            "tipo",
            "fecha_operacion"
        ]
    }