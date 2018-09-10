from django import forms
from django.db.models import Q
from .models import Pet, Person, AdoptionApplication, PetCharacteristic
from .mixins import UserInjectionFormMixin, FormControlWidgetMixin
from dal import autocomplete
from django.forms import inlineformset_factory
# from datetimewidget.widgets import DateWidget


class PetCharacteristicForm(forms.ModelForm):

    class Meta:
        model = PetCharacteristic
        fields = [
            'key', 'value',
        ]
        labels = {
            'key': 'nombre', 'value': 'valor',
        }
        exclude = ()


PetCharacteristicFormSet = inlineformset_factory(
    Pet, PetCharacteristic, form=PetCharacteristicForm)


"""formset = PetCharacteristicFormSet(
        initial=[{'key': 'color', 'value': "rojo", }])"""


class PetForm(UserInjectionFormMixin, FormControlWidgetMixin, forms.ModelForm):

    class Meta:
        model = Pet
        fields = [
            'name', 'vaccine', 'sex', 'age', 'rescue_date'
        ]
        labels = {
            'name': "Nombre",
            'vaccine': "Vacunas",
            'sex': "Sexo",
            'age': "Edad aproximada",
            'rescue_date': "Fecha de rescate",
        }

        widgets = {
            # 'people': autocomplete.ModelSelect2(url="refuge:people_autocomplete"),
            'vaccine': autocomplete.ModelSelect2Multiple(url="refuge:vaccine_autocomplete")
            # 'rescue_date':  DateWidget(options=dateTimeOptions)
        }


class PersonForm(FormControlWidgetMixin, forms.ModelForm):
    class Meta:
        model = Person

        fields = [
            'email', 'name', 'last_name', 'age', 'phone', 'home',
        ]
        labels = {
            'name': "Nombre",
            'last_name': "Apellidos",
            'age': "Edad",
            'phone': "Telefono",
            'email': "Correo Electronico",
            'home': "Domicilio",
        }


class AdoptionForm(UserInjectionFormMixin, FormControlWidgetMixin, forms.ModelForm):
    pets = forms.ModelMultipleChoiceField(
        # widget=autocomplete.ModelSelect2Multiple(url="refuge:pet_autocomplete"),
        queryset=Pet.objects.all())

    class Meta:
        model = AdoptionApplication

        fields = [
            'reasons',
        ]
        labels = {
            'reasons': "Razon para Adoptar",
        }
        widgets = {
        }

    def __init__(self, *args, **kwargs):
        self.person = kwargs.pop('person', None)
        super().__init__(*args, **kwargs)
        person_query = Q(person__isnull=True)
        if self.person is not None:
            person_query |= Q(person=self.person)
        self.fields['pets'].queryset = Pet.objects.filter(person_query)

    def save(self, commit=True, person=None):
        adoptionapplication = super().save(commit=False)
        if person:
            adoptionapplication.person = person
            self.person = person
        else:
            adoptionapplication.person = self.person
        adoptionapplication.save()
        pets = self.cleaned_data['pets']
        pets.update(person=self.person)
        return adoptionapplication
