from django.contrib.auth.backends import BaseBackend
from .models import User

class MongoBackend(BaseBackend):

    def authenticate(self, request, correo=None, password=None):
        try:
            user=User.objects.get(correo=correo)
            if user.checkPassword(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None        