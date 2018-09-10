from django import forms
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.mixins import AccessMixin
from usuario.models import UserWebSocketSession
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy


class UserFormInjectedViewMixin(object):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class LoginSessionRequiredMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        token = request.session.get('session_user_token')
        ws_session = UserWebSocketSession.objects.get(token=token)

        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not ws_session.session_two_steps:
            return HttpResponseRedirect(reverse_lazy('refuge:has_not_permits'))
        return super().dispatch(request, *args, **kwargs)


class UserOwnershipMixin(UserPassesTestMixin):

    def test_func(self):
        self.object = self.get_object()
        return self.object.created_by == self.request.user


class UserInjectionFormMixin(object):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.created_by = self.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class FormControlWidgetMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fname in self.fields:
            if isinstance(self.fields[fname].widget, forms.CheckboxSelectMultiple):
                continue
            self.fields[fname].widget.attrs.update({'class': 'form-control'})
