#Para manejar modelos de mongo
from mongoengine import Document, StringField, EmailField, DateTimeField
from django.contrib.auth.hashers import make_password, check_password
from cryptography.fernet import Fernet
from datetime import datetime, timedelta, timezone
import os
# Create your models here.
fernetKey = os.environ.get("FERNET_KEY")
cipher=Fernet(fernetKey)

#modelo de usuario
class User(Document):
    nombreCompleto = StringField(required=True)
    identidad = StringField(required=True, unique=True)
    tipoUsuario = StringField(required=True, choices=["cliente", "admin"])
    correo = EmailField(required=True, unique=True)
    telefono = StringField(required=True)
    cuentaBanco = StringField(required=False)
    nombreBanco = StringField(required=False)
    password = StringField(required=True)

    meta = {"collection": "users"}

    # Cifrado de cuentas bancarias
    def setCuentaBanco(self, cuenta):
        self.cuentaBanco = cipher.encrypt(cuenta.encode()).decode()

    def getCuentaBanco(self):
        return cipher.decrypt(self.cuentaBanco.encode()).decode()

    # Cifrado de contraseñas
    def setPassword(self, pswd):
        self.password = make_password(pswd)

    def checkPassword(self, pswd):
        return check_password(pswd, self.password)

    # Compatibilidad con Django Auth
    @property
    def is_authenticated(self):
        return True

    @property
    def pk(self):
        return str(self.id)

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

#Modelo para la recuperación de la cuenta
class PasswordResetCode(Document):
    correo= EmailField(required=True)
    codigo= StringField(required=True)
    createdAt= DateTimeField(default=lambda: datetime.now(timezone.utc))
    meta={
        "collection":"password_reset_codes",
        "indexes": [
            {"fields":["correo"]},
            {"fields":["createdAt"], "expireAfterSeconds":600}
        ]
    }        

    def checkCode(self, code):
        if datetime.now(timezone.utc)-self.createdAt>timedelta(minutes=10):
            return False
        return check_password(code, self.codigo)
    
class Request(Document):
    telefono = StringField(required=True)
    nombreCompleto= StringField(required=True)    