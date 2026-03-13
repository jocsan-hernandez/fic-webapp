import random
from django.contrib.auth.hashers import make_password

def generarCodigo():
    codigo = "{:06d}".format(random.randint(0, 999999))
    codigoHash= make_password(codigo)
    return codigo, codigoHash