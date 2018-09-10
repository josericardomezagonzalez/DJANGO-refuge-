from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserForm(UserCreationForm):

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
        ]
        labels = {
            'username': "Nombre de usuario",
            'first_name': "Nombre de pila",
            'last_name': "Apellidos",
            'email': "Correo",

        }

"""    def save(self, commit=True):
        user = super().save(commit=True)
        user_session = UserSession(user=user, number_active_sessions=0)
        user_session.save()
        return user
"""