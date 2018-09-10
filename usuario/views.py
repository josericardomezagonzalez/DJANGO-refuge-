from django.contrib.auth.models import User
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import UserForm
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.views import APIView
from .serializers import UserSerializer
import json
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from .models import UserWebSocketSession
from .message import publish
from django.contrib.auth.views import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


def customlogout(request):
    token = request.session.get('session_user_token', None)
    if token:
        session_user = UserWebSocketSession.objects.get(token=token)
        session_user.session_two_steps = False
        session_user.active_websocket = False
        session_user.save()

    return logout(request)


class CustomLoginView(LoginView):
    template_name = 'index.html'
    success_url = reverse_lazy("refuge:index")

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        valid = True

        if (request.method == 'POST' and request.POST['username'] and
                request.POST['password']):

            if request.session.get('session_user_token') is None:
                session_user = UserWebSocketSession.create_session_user(
                    user=request.user)
                request.session['session_user_token'] = session_user.token
                two_step = session_user.session_two_steps
                port = session_user.port
                request.session['session_user_two_steps'] = two_step
                request.session['session_user_port'] = port
                if not two_step:  # notifica al usuario que se ha iniciado otra sesion
                    publish(f'question_the_user.{session_user.user.id}',
                            {'user_id': session_user.user.id,
                             'token': session_user.token})
            else:
                token = request.session.get('session_user_token')
                session_user = UserWebSocketSession.objects.get(token=token)
                success = UserWebSocketSession.objects.filter(
                    user=session_user.user, session_two_steps=True).count() == 0
                if session_user.locked:
                    valid = False
                elif success:
                    valid = True
                    session_user.session_two_steps = True
                    session_user.save()
                session_user.session_two_steps = True
                session_user.save()
            two_step = session_user.session_two_steps
        else:  # metodo GET
            two_step = True

        if True:
            return response
        elif not valid:  # usuario bloqueado no acceso al sistema
            return HttpResponseRedirect(reverse_lazy('logout'))
        return HttpResponseRedirect(reverse_lazy('user:waiting_page'))


def user(request):
    return render(request, 'people/user_list.html')


def list(request):
    user = serializers.serialize('json', User.objects.all())
    return HttpResponse(user, content_type='application/json')


class UserRegistry(CreateView):
    model = User
    template_name = 'user/user_registry.html'
    form_class = UserForm
    success_url = reverse_lazy("login")

    def post(self, request, *arg, **kwargs):

        form = self.get_form()

        if form.is_valid():
            user = form.save()
            self.object = user
            return HttpResponseRedirect(self.get_success_url())
        else:
            kwargs['form'] = form

            return self.render_to_response(kwargs)


def user_session_token_authentication(request):
    first = False
    response = {'valid': False, 'first': first}
    token = request.GET.get('token', None)
    session_user = UserWebSocketSession.objects.filter(token=token)
    confirmation = session_user.exists()
    if confirmation:
        session_user = session_user.first()
        if not session_user.active_websocket and not session_user.locked:
            first = UserWebSocketSession.objects.filter(user=session_user.user,
                                                        active_websocket=True).count() == 0
            session_user.active_websocket = True
            session_user.save()
        response = {'valid': confirmation, 'first': first}

    return JsonResponse(response)

# confimacion de el usuario a una nueva session True o False


def user_session_confirm_token(request):
    response = {'valid': False}
    token = request.GET.get('token', None)
    campaign_id = request.GET.get('campaign_id', None)
    # si exite campaign id evaluar que esa campaña pertenesca a el usuario
    session_user = UserWebSocketSession.objects.filter(token=token)
    token_origin = request.GET.get('token_origin', None)
    valid_token_origin = UserWebSocketSession.objects.filter(
        token=token_origin).exists()
    valid_token_new = session_user.exists()
    session_user = session_user.get()

    if (not session_user.locked and not session_user.session_two_steps and
            valid_token_origin and valid_token_new):
        confirm = response_user = request.GET.get('confirm', None)
        if confirm == 'YES':
            session_user.session_two_steps = True
            response = {'valid': True}
        else:
            session_user.locked = True
        session_user.save()
        publish(f"session_confirm.{session_user.user.id}", {})
        publish(f'success_session_redirect.{session_user.token}',
                {'success': response["valid"]})

    return JsonResponse(response)



@login_required
def view_waiting_page(request):
    return render(request, 'user/waiting_page.html')


@login_required
def view_has_not_permits(request):
    return render(request, 'user/has_not_permits.html')


class UserAPI(APIView):
    serializers = UserSerializer

    def get(seft, request, format=None):
        list = User.objects.all()
        response = seft.serializers(list, many=True)

        return HttpResponse(json.dumps(response.data), content_type='application/json')

