from unittest.mock import patch, Mock
import unittest
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.http import HttpRequest
from .models import Pet, Person, AdoptionApplication
from .views import PetCreateView, PetUpdateView, AdoptionCreateView, AdoptionUpdateView
from django.utils.crypto import get_random_string

create_pet = PetCreateView.as_view()
# create_pet(request)
update_pet = PetUpdateView.as_view()
# update_pet(request, **{'pk': 1})

data_pet_caract = {'petcharacteristic_set-TOTAL_FORMS': '3',
                   'petcharacteristic_set-INITIAL_FORMS': '0',
                   'petcharacteristic_set-MIN_NUM_FORMS': '0',
                   'petcharacteristic_set-MAX_NUM_FORMS': '1000',
                   'petcharacteristic_set-0-key': '',
                   'petcharacteristic_set-0-value': '',
                   'petcharacteristic_set-0-id': '',
                   'petcharacteristic_set-0-pet': '',
                   'petcharacteristic_set-1-key': '',
                   'petcharacteristic_set-1-value': '',
                   'petcharacteristic_set-1-id': '',
                   'petcharacteristic_set-1-pet': '',
                   'petcharacteristic_set-2-key': '',
                   'petcharacteristic_set-2-value': '',
                   'petcharacteristic_set-2-id': '',
                   'petcharacteristic_set-2-pet': '',
                   }


@patch('refuge.views.PetForm')
@patch('refuge.views.PetCharacteristicFormSet')
class PetCreateViewUnitTest(unittest.TestCase):

    def setUp(self):
        user = User(username=get_random_string(length=6))
        user.set_password('love rock and matal and more')
        user.save()
        self.data_pet = {'name': 'firulais', 'sex': 'macho', 'created_by': user,
                         'age': 1, 'rescue_date': '2018-1-1', 'vaccine': []}
        self.request = HttpRequest()
        self.request.POST = dict({}, **self.data_pet, **data_pet_caract)
        self.request.user = user
        self.request.method = "POST"

    def test_passes_POST_data_to_pet_create(self, mockPetCharacteristicFormSetClass,
                                            mockPetFormClass):
        response = create_pet(self.request)
        self.assertEqual(response.url, '/pet/list/')
        # mockPetCharacteristicFormSetClass.assert_called_once_with(data=self.request.POST)
        # mockPetFormClass.assert_called_once_with(data=self.request.POST)

    def test_pet_create(self, mockPetCharacteristicFormSetClass,
                        mockPetFormClass):
        mock_form = mockPetFormClass.return_value
        mock_form.is_valid.return_value = True
        response = create_pet(self.request)
        self.assertEqual(response.url, '/pet/list/')
        # mock_form.save.assert_called_once_with(data=None)


@patch('refuge.views.Pet')
@patch('refuge.views.PetForm')
@patch('refuge.views.PetCharacteristicFormSet')
class PetUpdateViewUnitTest(unittest.TestCase):

    def setUp(self):
        user = User(username=get_random_string(length=6))
        user.set_password('love rock and matal and more')
        user.save()
        self.data_pet = {'name': 'gamina', 'sex': 'macho', 'created_by': user,
                         'age': 1, 'rescue_date': '2018-1-1'}
        self.request = HttpRequest()
        self.request.POST = dict({}, **self.data_pet, **data_pet_caract)
        self.request.user = user
        self.request.method = "POST"

    def test_passes_POST_data_to_pet_update(self, mockPetCharacteristicFormSetClass,
                                            mockPetFormClass, mockPetClass):
        pet = Pet(**self.data_pet)
        pet.save()
        response = update_pet(self.request, **{'pk': f'{pet.id}'})
        self.assertEqual(response.url, '/pet/list/')
        # mockPetCharacteristicFormSetClass.assert_called_once_with(data=self.request.POST)
        # mockPetFormClass.assert_called_once_with(self.request.POST)

    def test_saves_form_pet_update_if_valid_data(self, mockPetCharacteristicFormSetClass,
                                                 mockPetFormClass, mockPetClass):
        mock_form = mockPetFormClass.return_value
        mock_form.is_valid.return_value = True
        pet = Pet(**self.data_pet)
        pet.save()
        response = update_pet(self.request, **{'pk': f'{pet.id}'})
        self.assertEqual(response.url, '/pet/list/')
        # mock_form.save.assert_called_once_with(data=None)


class PetCreateViewUnitTest2(unittest.TestCase):

    def setUp(self):
        user = User.objects.create_user(
            username=get_random_string(length=6), email='jacob@…', password='top_secret')
        self.data_pet = {'name': 'xokore', 'sex': 'macho', 'created_by': user,
                         'age': 1, 'rescue_date': '2018-1-1'}
        self.request = HttpRequest()
        self.request.POST = dict({}, **self.data_pet, **data_pet_caract)
        self.request.user = user
        self.request.method = "POST"

    def test_get_formset_kwargs_get(self):
        pet_view = PetCreateView()
        pet_view.request = HttpRequest()
        pet_view.request.method = 'GET'
        pet_view.user = self.request.user
        result = pet_view.get_formset_kwargs()
        self.assertTrue(result == {})

    def test_get_formset_kwargs_post(self):
        pet_view = PetCreateView()
        pet_view.request = self.request
        result = pet_view.get_formset_kwargs()
        self.assertEqual(result['data'], self.request.POST)

    def test_gets_correct_object(self):
        pet_view = PetCreateView()
        pet_view.request = self.request
        response = pet_view.post(self.request)
        # print(pet_view.get_context_data())
        # print(pet_view.get_formset_kwargs())
        # print(pet_view.get_formset())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(pet_view.object == pet_view.get_formset_kwargs()['instance'])


class PetUpdateViewUnitTest2(unittest.TestCase):

    def setUp(self):
        user = User.objects.create_user(
            username=get_random_string(length=6), email='jacob@…', password='top_secret')
        self.data_pet = {'name': 'xokore', 'sex': 'macho', 'created_by': user,
                         'age': 1, 'rescue_date': '2018-1-1'}
        self.request = HttpRequest()
        self.request.POST = dict({}, **self.data_pet, **data_pet_caract)
        self.request.user = user
        self.request.method = "POST"

    def test_gets_correct_object(self):
        pet = Pet(**self.data_pet)
        pet.save()
        pet_view = PetUpdateView()
        pet_view.kwargs = self.request.POST
        pet_view.request = self.request
        response = pet_view.post(self.request, **{'pk': f'{pet.id}'})
        # print(pet_view.get_context_data())
        # print(pet_view.get_formset_kwargs())
        # print(pet_view.get_formset())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(pet_view.object ==
                        pet_view.get_formset_kwargs()['instance'])


class AdoptionCreateViewUnitTest(unittest.TestCase):

    def setUp(self):
        user = User.objects.create_user(
            username=get_random_string(length=6), email='jacob@…', password='top_secret')

        data_pet = {'name': 'xokore', 'sex': 'macho', 'created_by': user,
                    'age': 1, 'rescue_date': '2018-1-1'}
        data_person = {'name': 'juan', 'last_name': 'robles', 'age': 15,
                       'email': 'juan@gmail.com', 'home': 'calle brava',
                       'phone': '9514241244'}

        data_adoption = {'reasons': 'no quiero mascotas'}
        pet = Pet(**data_pet)
        pet.save()
        # validacion no se puede crear una adopcion si no se elije una mascota
        self.request = HttpRequest()
        self.request.POST = dict({'pets': []}, **data_person, **data_adoption)
        self.request.user = user
        self.request.method = "POST"

    def test_gets_correct_object(self):
        adoption_view = AdoptionCreateView()
        adoption_view.kwargs = self.request.POST
        adoption_view.request = self.request
        response = adoption_view.post(self.request)
        self.assertEqual(response.status_code, 200)


class AdoptionUpdateViewUnitTest(unittest.TestCase):

    def setUp(self):
        user = User.objects.create_user(
            username=get_random_string(length=6), email='jacob@…', password='top_secret')

        data_pet = {'name': 'xokore', 'sex': 'macho', 'created_by': user,
                    'age': 1, 'rescue_date': '2018-1-1'}
        data_person = {'name': 'juan', 'last_name': 'robles', 'age': 15,
                       'email': 'juan@gmail.com', 'home': 'calle brava',
                       'phone': '9514241244'}

        data_adoption = {'reasons': 'no quiero mascotas'}
        person = Person(**data_person)
        person.save()
        self.adoption = AdoptionApplication(person=person,
                                            reasons='por q si solo dame mi maldito perro',
                                            created_by=user)
        self.adoption.save()
        pet = Pet(**data_pet)
        pet.save()
        # validacion no se puede crear una adopcion si no se elije una mascota
        self.request = HttpRequest()
        self.request.POST = dict({'pets': []}, **data_person, **data_adoption)
        self.request.user = user
        self.request.method = "POST"

    def test_gets_correct_object(self):
        adoption_view = AdoptionUpdateView()
        adoption_view.kwargs = self.request.POST
        adoption_view.request = self.request
        response = adoption_view.post(self.request, **{'pk': f'{self.adoption.id}'})
        self.assertEqual(response.status_code, 200)
