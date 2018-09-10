from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from .forms import PetForm, AdoptionForm, PersonForm, PetCharacteristicFormSet
from django.urls import reverse_lazy
from .models import Pet, Person, AdoptionApplication, Vaccine
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core import serializers
from .mixins import UserFormInjectedViewMixin, UserOwnershipMixin, LoginSessionRequiredMixin
from django.contrib.auth.decorators import login_required
from dal import autocomplete
from django.http import HttpResponse
from django.db.models import Q
from usuario.models import UserWebSocketSession
from usuario.message import publish
import time


def session_requerid(funtion_view):
    def funtion(request):
        token = request.session.get('session_user_token', None)
        if token:
            ws_session = UserWebSocketSession.objects.get(token=token)
            if ws_session.session_two_steps:
                return funtion_view(request)
        if not request.user.is_authenticated:
            return funtion_view(request)
        # redirecciona a una pagina donde se le diga q no tiene permisos
        return HttpResponseRedirect(reverse_lazy('user:has_not_permits'))
    return funtion


@session_requerid
@login_required
def index(request):
    token = request.session['session_user_token']
    two_steps = UserWebSocketSession.objects.get(
        token=token).session_two_steps
    if request.session.get('session_user_two_steps', None) is not None:
        request.session['session_user_two_steps'] = two_steps
    return render(request, 'pet/index.html')


class PetListView(LoginSessionRequiredMixin, ListView):
    model = Pet
    template_name = 'pet/pet_list.html'
    paginate_by = 10

    def get_queryset(self):
        return Pet.objects.filter(created_by=self.request.user).order_by('id').reverse()


class PetCreateUpdateMixin(object):
    model = Pet
    form_class = PetForm
    template_name = 'form/form.html'
    success_url = reverse_lazy('refuge:pet_list')
    formset_class = PetCharacteristicFormSet

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['formset'] = self.get_formset()
        return kwargs

    def get_formset_kwargs(self):
        result = {}
        if self.request.method == 'POST':
            result['data'] = self.request.POST

        if hasattr(self, 'object') and self.object is not None:
            result['instance'] = self.object
        return result

    def get_formset(self):
        return self.formset_class(**self.get_formset_kwargs())

    def post(self, request, *arg, **kwargs):
        form = self.get_form()
        formset = self.get_formset()

        if form.is_valid() and formset.is_valid():
            pet = form.save()
            formset.instance = pet
            formset.save()
            self.object = pet
            return HttpResponseRedirect(self.get_success_url())
        else:
            kwargs['form'] = form
            kwargs['formset'] = formset
            return self.render_to_response(kwargs)


class PetCreateView(LoginSessionRequiredMixin, UserFormInjectedViewMixin,
                    PetCreateUpdateMixin, CreateView):
    pass


class PetUpdateView(LoginSessionRequiredMixin, UserOwnershipMixin,
                    PetCreateUpdateMixin, UserFormInjectedViewMixin,
                    UpdateView):
    pass


class PetDeleteView(LoginSessionRequiredMixin, UserOwnershipMixin, DeleteView):
    model = Pet
    form_class = PetForm
    template_name = 'pet/pet_delete.html'
    success_url = reverse_lazy('refuge:pet_list')


class AdoptionListView(LoginSessionRequiredMixin, ListView):
    model = AdoptionApplication
    template_name = 'adoption/AdoptionList.html'

    def get_queryset(self):
        return AdoptionApplication.get_adoption(self.request.user)


class AdoptionCreateUpdateMixin(object):
    model = AdoptionApplication
    template_name = 'form/form.html'
    form_class = AdoptionForm
    form2_class = PersonForm

    success_url = reverse_lazy('refuge:adoption_list')

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['form2'] = self.get_form2()
        return kwargs

    def get_form2_kwargs(self):
        result = {}
        if self.request.method == 'POST':
            result['data'] = self.request.POST
        person_pk = self.request.POST.get('person_pk', None)
        self.pets = self.request.POST.get('pets', None)
        if hasattr(self, 'object') and self.object is not None:
            result['instance'] = self.object.person
            self.person = self.object.person
        elif person_pk:
            result['instance'] = Person.objects.get(id=person_pk)
            self.person = result['instance']
        return result

    def get_form2(self):
        return self.form2_class(**self.get_form2_kwargs())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object') and self.object is not None:
            kwargs['person'] = self.object.person
        elif hasattr(self, 'person'):
            kwargs['person'] = self.person
        return kwargs

    def post(self, request, *arg, **kwargs):
        form2 = self.get_form2()
        form = self.get_form()

        if form.is_valid() and form2.is_valid():
            person = form2.save()
            adoption = form.save(person=person)
            self.object = adoption
            return HttpResponseRedirect(self.get_success_url())
        else:
            kwargs['form'] = form
            kwargs['form2'] = form2
            return self.render_to_response(kwargs)


class AdoptionCreateView(LoginSessionRequiredMixin, UserFormInjectedViewMixin,
                         AdoptionCreateUpdateMixin, CreateView):
    # def get_success_url(self):
    #    return reverse('refuge:adoption_update', kwargs={'pk': self.object.id})
    pass


class AdoptionUpdateView(LoginSessionRequiredMixin, UserFormInjectedViewMixin, UserOwnershipMixin,
                         AdoptionCreateUpdateMixin, UpdateView):
    pass


class AdoptionDeleteView(LoginSessionRequiredMixin, UserOwnershipMixin, DeleteView):

    model = AdoptionApplication
    template_name = 'adoption/adoption_delete.html'
    success_url = reverse_lazy('refuge:adoption_list')


class VaccineAutocompleteView(LoginSessionRequiredMixin, autocomplete.Select2QuerySetView):

    def get_result_label(self, item):
        return item.name

    def get_queryset(self):
        result = Vaccine.objects.all()
        if self.q:
            result = Vaccine.objects.filter(
                name__istartswith=self.q).order_by('name')
        return result


class PersonAutocompleteView(LoginSessionRequiredMixin, autocomplete.Select2QuerySetView):
    def get_result_label(self, item):
        return '{} {}'.format(item.name, item.last_name)

    def get_queryset(self):
        result = Person.objects.all()
        if self.q:
            result = Person.objects.filter(
                name__istartswith=self.q).order_by('name')
        return result


class PetAutocompleteView(LoginSessionRequiredMixin, autocomplete.Select2QuerySetView):
    def get_result_label(self, item):
        return f'name :{item.name} sex: {item.sex}'

    def get_queryset(self):
        person_query = Q(person__isnull=True)
        if self.person is not None:
            person_query |= Q(person=self.person)
        result = Pet.objects.filter(person_query)
        result = Pet.objects.all()
        if self.q:
            person_query |= Q(name__istartswith=self.q)
            result = Pet.objects.filter(person_query).order_by('name')
        return result


@session_requerid
@login_required
def list_pet(request):
    pets = serializers.serialize('json', Pet.objects.all().order_by('name'))
    return JsonResponse(pets, safe=False)


@session_requerid
@login_required
def list_person(request):
    email = request.GET.get('email')
    people = {}
    if email:
        people = Person.objects.filter(email=email)
    if not people:
        people = {}

    people = serializers.serialize('json', people)

    return HttpResponse(people, content_type='application/json')


@session_requerid
@login_required
def view_person(request):
    return render(request, 'people/people_list.html')


@login_required
def create_instance_example(request):

    token = request.GET.get('token')
    time.sleep(5)
    publish(f'instance_creationevent.{token}', {'message': 'Register domain.'})
    time.sleep(3)
    publish(f'instance_creationevent.{token}', {'message': 'Set name servers.'})
    time.sleep(3)
    publish(f'instance_creationevent.{token}', {'message': 'Start instace.'})
    time.sleep(3)
    publish(f'instance_creationevent.{token}', {'message': 'Allocation new ip address.'})
    time.sleep(2)
    publish(f'instance_creationevent.{token}', {'message': 'Waiting for instance setup.'})
    time.sleep(3)
    publish(f'instance_creationevent.{token}', {'message': 'Associated ip to instance.'})
    time.sleep(4)
    publish(f'instance_creationevent.{token}', {'message': 'Updating domain record sets.'})
    time.sleep(3)
    publish(f'instance_creationevent.{token}', {'message': 'Done.'})
    req = serializers.serialize('json', {})

    return HttpResponse(req, content_type='application/json')

# publish('instance_creationevent.{}'.format(
#                         token), {'message': 'Register domain.'})