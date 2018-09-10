from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.crypto import get_random_string
from random import randint


def generate_token():
    return get_random_string(50)


def generate_port():
    return randint(3000, 3003)


# Create your models here.
class UserWebSocketSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(
        max_length=50, unique=True, default=generate_token)
    active_websocket = models.BooleanField(default=False)
    session_two_steps = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    port = models.PositiveIntegerField(default=generate_port)

    def __str__(self):
        return self.user.username

    @classmethod
    def create_session_user(cls, user):
        filter_user = Q(user=user) & Q(session_two_steps=True)
        session_list = cls.objects.filter(filter_user)
        session_user = cls(user=user)
        # creara un usuario con session_two = True si no hay uno
        if session_list.count() == 0:
            session_user = cls(user=user, session_two_steps=True)
        session_user.save()
        return session_user
