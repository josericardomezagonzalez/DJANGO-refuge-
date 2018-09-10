from django.contrib.auth.models import User
from django.test import TestCase
from .models import Pet, Person, Vaccine, AdoptionApplication, PetCharacteristic
from django.urls import reverse
from django.utils import timezone

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


class BaseTestWithLoginMixin(object):

    def setUp(self):
        u = User(username='claustofo')
        u.set_password('love rock and matal and more')
        u.save()
        self.user = u
        self.client.force_login(u)


class IndexTest(BaseTestWithLoginMixin, TestCase):

    def test_index_load(self):
        response = self.client.get(reverse('refuge:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/pet/')


class PetCreateViewTest(BaseTestWithLoginMixin, TestCase):

    def test_pet_creation_valid_data_user_has_permission(self):
        # has 0 vaccine
        vaccine = Vaccine(name='rabioli')
        vaccine.save()
        vaccine1 = Vaccine(name='zarnoli')
        vaccine1.save()

        data = {'name': 'chilaquil', 'sex': 'macho',
                'age': '2', 'vaccine': [], 'rescue_date': '2018-1-1'}
        response = self.client.post(
            reverse('refuge:pet_create'), dict({}, **data, **data_pet_caract), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('refuge:pet_list'))
        data.pop('vaccine')
        pet_qs = Pet.objects.filter(**data)
        self.assertTrue(pet_qs.count() == 1)
        pet = pet_qs.first()
        self.assertTrue(pet.vaccine.count() == 0)
        self.assertTrue(PetCharacteristic.objects.count() == 0)
        # has 1 vaccine
        data = {'name': 'chapulin', 'sex': 'macho',
                'age': '2', 'vaccine': [vaccine.id], 'rescue_date': '2018-1-1'}
        data_pet_caract['petcharacteristic_set-0-key'] = 'ojos'
        data_pet_caract['petcharacteristic_set-0-value'] = 'bien chulos'
        response = self.client.post(
            reverse('refuge:pet_create'), dict({}, **data, **data_pet_caract), follow=True)

        data.pop('vaccine')
        pet_qs = Pet.objects.filter(**data)
        self.assertTrue(pet_qs.count() == 1)
        pet = pet_qs.first()
        self.assertTrue(pet.vaccine.count() == 1)
        self.assertTrue(pet.vaccine.first().id == vaccine.id)
        self.assertTrue(PetCharacteristic.objects.count() == 1)
        petcaract = PetCharacteristic.objects.get(key='ojos')
        self.assertEqual(petcaract.value, 'bien chulos')
        response = self.client.get(reverse('refuge:pet_list'))
        self.assertQuerysetEqual(response.context['object_list'],
                                 ['<Pet: chapulin>', '<Pet: chilaquil>']
                                 )

        # has 2 vaccine
        data = {'name': 'pelusa', 'sex': 'macho',
                'age': '2', 'vaccine': [vaccine.id, vaccine1.id],
                'rescue_date': '2018-1-1'}
        data_pet_caract['petcharacteristic_set-1-key'] = 'color de pelo'
        data_pet_caract['petcharacteristic_set-1-value'] = 'blanco con negro'
        # data_pet_caract['petcharacteristic_set-INITIAL_FORMS'] = '1'
        response = self.client.post(
            reverse('refuge:pet_create'), dict({}, **data, **data_pet_caract), follow=True)
        data.pop('vaccine')
        vaccinelist = [vaccine, vaccine1]
        pet_qs = Pet.objects.filter(**data)
        self.assertTrue(pet_qs.count() == 1)
        pet = pet_qs.first()
        self.assertTrue(pet.vaccine.count() == 2)
        for v, v1 in zip(vaccinelist, pet.vaccine.all()):
            self.assertTrue(v.id == v1.id)
        self.assertTrue(PetCharacteristic.objects.filter(
            pet=pet.id).count() == 2)
        petcaract = PetCharacteristic.objects.get(key='color de pelo')
        self.assertEqual(petcaract.value, 'blanco con negro')
        response = self.client.get(reverse('refuge:pet_list'))
        self.assertQuerysetEqual(response.context['object_list'],
                                 ['<Pet: pelusa>', '<Pet: chapulin>', '<Pet: chilaquil>']
                                 )

    def test_pet_creation_invalid_data_has_permission(self):

        vaccine = Vaccine(name='rabioli')
        vaccine.save()
        person = Person(name='matamorra', last_name='xoxo', age='23',
                        email='coaa@gmai1', home='calle brava', phone='123213312')
        person.save()
        response = self.client.post(reverse('refuge:pet_create'),
                                    dict({'name': 'chilaquil', 'sex': 'macho',
                                          'age': '2', 'vaccine': vaccine.id,
                                          'rescue_date': '2018-1'}, **data_pet_caract),
                                    follow=True)

        self.assertEqual(response.request['PATH_INFO'], '/pet/create/')
        self.assertIs(Pet.objects.first(), None)
        self.assertTrue(PetCharacteristic.objects.count() == 0)

    def test_pet_creation_has_not_login(self):
        self.client.logout()

        vaccine = Vaccine(name='rabioli')
        vaccine.save()
        person = Person(name='matamorra', last_name='xoxo', age='23',
                        email='coaa@gmail2.com', home='calle brava', phone='123213312')
        person.save()
        response = self.client.post(reverse('refuge:pet_create'),
                                    dict({'name': 'chilaquil',
                                          'sex': 'macho', 'age': '2',
                                          'vaccine': vaccine.id,
                                          'rescue_date': '2018-1-1'},
                                         **data_pet_caract), follow=True)

        self.assertEqual(response.request['PATH_INFO'], '/accounts/login/')
        self.assertIs(Pet.objects.first(), None)
        self.assertTrue(PetCharacteristic.objects.count() == 0)


class AdoptionCreateViewTest(BaseTestWithLoginMixin, TestCase):

    def test_adoption_creation_valid_data_has_permission(self):
        data_person = {'name': 'juan', 'last_name': 'robles', 'age': 15,
                       'email': 'juan@gmail.com', 'home': 'calle brava',
                       'phone': '9514241244'}

        data_adoption = {'reasons': 'no quiero mascotas'}

        data_pet = {'name': 'firulais', 'sex': 'macho', 'created_by': self.user,
                    'age': 1, 'rescue_date': timezone.now()}

        pet = Pet(**data_pet)
        pet.save()
        # validacion no se puede crear una adopcion si no se elije una mascota
        response = self.client.post(reverse('refuge:adoption_create'),
                                    dict({'pets': []}, **data_person, **data_adoption),
                                    follow=True)

        self.assertEqual(
            response.request['PATH_INFO'], '/pet/adoption/create/')
        self.assertTrue(AdoptionApplication.objects.count() is 0)
        self.assertTrue(Person.objects.count() is 0)

        data_person = {'name': 'antonio', 'last_name': 'robles', 'age': 15,
                       'email': 'antonio@gmail.com', 'home': 'calle brava',
                       'phone': '9514241244'}

        data_adoption = {'reasons': 'mas mascotas mas felicidad'}

        # validacion de que si se pueden adoptar dos mascotas
        response = self.client.post(reverse('refuge:adoption_create'),
                                    dict({'pets': [pet.id]}, **data_person, **data_adoption),
                                    follow=True)

        data_pet.pop('rescue_date')

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('refuge:adoption_list'))
        adoption = AdoptionApplication.objects.get()
        person = Person.objects.get()
        pet_qs = Pet.objects.get(id=pet.id)
        dict(data_adoption, **{'person': person})

        for key, value in data_adoption.items():
            self.assertEqual(getattr(adoption, key), value)

        for key, value in data_pet.items():
            self.assertEqual(getattr(pet_qs, key), value)

        self.assertEqual(pet_qs.person, person)

        data_person = {'name': 'carlos', 'last_name': 'xoxo', 'age': 23,
                       'email': 'carlos@gmail.com', 'home': 'calle brava',
                       'phone': '123213312'}

        data_adoption = {'reasons': 'por que si'}

        data_pet = {'name': 'michi', 'sex': 'macho', 'created_by': self.user,
                    'age': 2, 'rescue_date': timezone.now()}
        pet = Pet(**data_pet)
        pet.save()
        data_pet.pop('rescue_date')
        data_pet2 = {'name': 'pelusa', 'sex': 'hembra', 'created_by': self.user,
                     'age': 2, 'rescue_date': timezone.now()}

        pet2 = Pet(**data_pet2)
        pet2.save()
        data_pet2.pop('rescue_date')

        # validacion de que si se pueden adoptar dos mascotas
        response = self.client.post(reverse('refuge:adoption_create'),
                                    dict({'pets': [pet.id, pet2.id]},
                                         **data_person, **data_adoption),
                                    follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('refuge:adoption_list'))
        person = Person.objects.filter(name='carlos').get()
        adoption = AdoptionApplication.objects.filter(person=person).get()
        pet_qs = Pet.objects.get(id=pet.id)
        pet2_qs = Pet.objects.get(id=pet2.id)
        dict(data_adoption, **{'person': person})
        for key, value in data_adoption.items():
            self.assertEqual(getattr(adoption, key), value)

        for key, value in data_pet.items():
            self.assertEqual(getattr(pet_qs, key), value)

        for key, value in data_pet2.items():
            self.assertEqual(getattr(pet2_qs, key), value)

        for key, value in data_person.items():
            self.assertEqual(getattr(person, key), value)

        self.assertEqual(pet_qs.person, person)
        self.assertEqual(pet2_qs.person, person)

        # validando adopcion de la misma mascota por otra person
        data_person = {'name': 'martin', 'last_name': 'xoxo', 'age': 25,
                       'email': 'martin@gmail.com', 'home': 'calle del pozo',
                       'phone': '922451515'}

        response = self.client.post(reverse('refuge:adoption_create'),
                                    dict({'pets': [pet.id, pet2.id]},
                                         **data_person, **data_adoption),
                                    follow=True,
                                    )
        self.assertTrue(AdoptionApplication.objects.count() is 2)
        self.assertTrue(Person.objects.count() is 2)
        # valida que las mascotas le siguen perteneciendo ala misma persona
        self.assertEqual(pet_qs.person, person)
        self.assertEqual(pet2_qs.person, person)

    def test_adoption_creation_invalid_data_has_permission(self):

        response = self.client.post(reverse('refuge:adoption_create'),
                                    {'name': '', 'last_name': 'xoxo', 'age': 'ttt',
                                     'email': 'coaa@gmail4.com', 'home': 'calle brava',
                                     'phone': '123213312',
                                     'reasons': 'por que si'}, follow=True)

        self.assertEqual(
            response.request['PATH_INFO'], '/pet/adoption/create/')
        self.assertIs(AdoptionApplication.objects.first(), None)

    def test_adoption_creation_valid_data_has_not_login(self):
        self.client.logout()

        response = self.client.post(reverse('refuge:adoption_create'),
                                    {'name': 'carlos', 'last_name': 'xoxo', 'age': '23',
                                     'email': 'coaa@gmail5.com', 'home': 'calle brava',
                                     'phone': '123213312',
                                     'reasons': 'por que si'}, follow=True)

        self.assertEqual(response.request['PATH_INFO'], '/accounts/login/')
        self.assertIs(AdoptionApplication.objects.first(), None)

    def test_adoption_creation_to_the_same_person_valid_data_has_login(self):

        self.client.force_login(self.user)
        person_data = {'name': 'enrique', 'last_name': 'xoxo', 'age': 23,
                       'email': 'enrique@gmail6.com', 'home': 'calle brava',
                       'phone': '123213312'}

        data_pet = {'name': 'manchas', 'sex': 'macho', 'created_by': self.user,
                    'age': 2, 'rescue_date': timezone.now()}

        pet = Pet(**data_pet)
        pet.save()
        person = Person(**person_data)
        person.save()

        data_adoption = {'reasons': 'hace falta mas carne'}
        # validando que no se puede crear una nueva adopcion con una persona
        # ya existen sin elegir una mascota

        data = dict({'person_pk': person.id, 'pets': []}, **data_adoption, **person_data)

        response = self.client.post(reverse('refuge:adoption_create'),
                                    data, follow=True)

        self.assertEqual(
            response.request['PATH_INFO'], '/pet/adoption/create/')

        self.assertTrue(AdoptionApplication.objects.count() is 0)

        person_data = {'name': 'carlos', 'last_name': 'xoxo', 'age': 23,
                       'email': 'coaa@gmail6.com', 'home': 'calle brava',
                       'phone': '123213312'}

        person = Person(**person_data)
        person.save()
        data_pet.pop('rescue_date')
        data_adoption = {'reasons': 'hace falta mas carne'}
        # seleleciona una mascota sin adoptar
        data = dict({'person_pk': person.id, 'pets': [pet.id]}, **data_adoption, **person_data)

        response = self.client.post(reverse('refuge:adoption_create'),
                                    data, follow=True)

        self.assertEqual(response.request['PATH_INFO'], '/pet/adoption/list/')
        adoption = AdoptionApplication.objects.get()

        for attri, value in person_data.items():
            self.assertEqual(getattr(adoption.person, attri), value)
        dict(data_adoption, **{'person': person})
        for attri, value in data_adoption.items():
            self.assertEqual(getattr(adoption, attri), value)
        pet = Pet.objects.get()
        self.assertEqual(pet.person, person)

        person_data = {'name': 'maria', 'last_name': 'xoxo', 'age': 13,
                       'email': 'maria@gmail.com', 'home': 'calle centro',
                       'phone': '123213312'}

        data_pet = {'name': 'pelusa', 'sex': 'hembra', 'created_by': self.user,
                    'age': 2, 'rescue_date': timezone.now()}
        pet2 = Pet(**data_pet)
        pet2.save()

        person2 = Person(**person_data)
        person2.save()
        data_adoption = {'reasons': 'hace falta mas carne'}

        # validacion de que no se puede adoptar una mascota sin persona y una con persona
        data = dict({'person_pk': person2.id, 'pets': [pet.id, pet2.id]},
                    **data_adoption, **person_data)

        response = self.client.post(reverse('refuge:adoption_create'),
                                    data, follow=True)

        self.assertEqual(
            response.request['PATH_INFO'], '/pet/adoption/create/')

        adoption = AdoptionApplication.objects.last()
        dict(data_adoption, **{'person': person2})
        for attri, value in data_adoption.items():
            self.assertEqual(getattr(adoption, attri), value)

        self.assertEqual(Pet.objects.first().person, person)

        self.assertTrue(Pet.objects.filter(
            name="pelusa").first().person is None)

        data_pet = {'name': 'camina', 'sex': 'hembra', 'created_by': self.user,
                    'age': 2, 'rescue_date': timezone.now()}
        pet3 = Pet(**data_pet)
        pet3.save()

        data_adoption = {'reasons': 'ahora si quiero mi mascota'}

        # validacion de se pueden adoptar dos mascotas
        data = dict({'person_pk': person2.id, 'pets': [pet2.id, pet3.id]},
                    **data_adoption, **person_data)

        response = self.client.post(reverse('refuge:adoption_create'),
                                    data, follow=True)

        self.assertEqual(
            response.request['PATH_INFO'], '/pet/adoption/list/')

        adoption = AdoptionApplication.objects.filter(
            reasons='ahora si quiero mi mascota').first()
        for attri, value in data_adoption.items():
            self.assertEqual(getattr(adoption, attri), value)
        pets = Pet.objects.all()
        self.assertEqual(pets.get(id=pet2.id).person, person2)
        self.assertEqual(pets.get(id=pet3.id).person, person2)

    def test_adoption_creation_to_the_same_person_valid_data_has_login_and_repeated_mail(self):

        self.client.force_login(self.user)
        person_data = {'name': 'carlos', 'last_name': 'xoxo', 'age': 23,
                       'email': 'coaa@gmail6.com', 'home': 'calle brava',
                       'phone': '123213312'}
        person = Person(**person_data)
        person.save()

        adoption_data = {'reasons': 'hace falta mas carne'}

        data = dict({}, **adoption_data, **person_data)

        response = self.client.post(reverse('refuge:adoption_create'),
                                    data, follow=True)

        self.assertEqual(
            response.request['PATH_INFO'], '/pet/adoption/create/')
        self.assertTrue(AdoptionApplication.objects.count() is 0)


class PetUpdateViewTest(BaseTestWithLoginMixin, TestCase):

    def test_update_pet_data_has_permissions(self):
        # 'petcharacteristic_set-0-DELETE' = 'on'
        data_pet_caract = {
            'petcharacteristic_set-TOTAL_FORMS': '3',
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

        vaccine = Vaccine(name='popocha')
        vaccine.save()
        pet = Pet(name='del buldog', sex='hembra', age='2',
                  created_by=self.user, rescue_date='2018-1-3')
        pet.save()
        pet.vaccine.add(vaccine)
        petcaract = PetCharacteristic(pet=pet, key='nariz', value='de bola')
        petcaract.save()
        response = self.client.get(reverse('refuge:pet_update', args=[pet.id]))
        self.assertEqual(response.context['object'], pet)
        self.assertEqual(len(response.context['formset']), 4)
        data_pet_caract['petcharacteristic_set-1-key'] = 'cara'
        data_pet_caract['petcharacteristic_set-1-value'] = 'de cuche'
        data_pet_caract['petcharacteristic_set-1-id'] = ''
        data_pet_caract['petcharacteristic_set-1-pet'] = f'{pet.id}'

        response = self.client.post(reverse('refuge:pet_update', args=[pet.id]),
                                    dict({'name': 'chilaquil',
                                          'sex': 'macho', 'age': 3,
                                          'vaccine': vaccine.id,
                                          'rescue_date': '2018-1-1'},
                                         **data_pet_caract), follow=True)

        attri = ['name', 'sex', 'age', 'vaccine']
        value = ['chilaquil', 'macho', 3, vaccine]
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('refuge:pet_list'))
        self.assertQuerysetEqual(
            response.context['object_list'],
            ['<Pet: chilaquil>']
        )
        response = self.client.get(reverse('refuge:pet_update', args=[pet.id]))
        self.assertEqual(response.context['object'], pet)
        self.assertEqual(len(response.context['formset']), 5)
        pet = Pet.objects.get()
        for a, v in zip(attri, value):
            if a == 'vaccine':
                self.assertEqual(pet.vaccine.get(id=vaccine.id), v)
            else:
                self.assertEqual(getattr(pet, a), v)
        self.assertTrue(PetCharacteristic.objects.filter(pet=pet).count() == 2)
        petcaract = PetCharacteristic.objects.get(key='cara')
        self.assertEqual(petcaract.value, 'de cuche')
        petcaract = PetCharacteristic.objects.get(key='nariz')
        self.assertEqual(petcaract.value, 'de bola')

        petcaract = PetCharacteristic.objects.filter(key="nariz").first()
        data_pet_caract['petcharacteristic_set-INITIAL_FORMS'] = '2'
        data_pet_caract['petcharacteristic_set-0-id'] = f'{petcaract.id}'
        data_pet_caract['petcharacteristic_set-0-pet'] = f'{pet.id}'
        data_pet_caract['petcharacteristic_set-0-DELETE'] = 'on'

        petcaract = PetCharacteristic.objects.filter(key="cara").first()
        data_pet_caract['petcharacteristic_set-1-id'] = f'{petcaract.id}'
        data_pet_caract['petcharacteristic_set-1-pet'] = f'{pet.id}'
        data_pet_caract['petcharacteristic_set-1-key'] = 'prueba update'
        data_pet_caract['petcharacteristic_set-1-value'] = 'algun Value'

        response = self.client.post(reverse('refuge:pet_update', args=[pet.id]),
                                    dict({'name': 'chilaquil',
                                          'sex': 'macho', 'age': 3,
                                          'vaccine': vaccine.id,
                                          'rescue_date': '2018-1-1'},
                                         **data_pet_caract), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('refuge:pet_list'))
        self.assertTrue(PetCharacteristic.objects.count() == 1)
        petcaract = PetCharacteristic.objects.get()
        self.assertEqual(petcaract.key, 'prueba update')
        self.assertEqual(petcaract.value, 'algun Value')
        response = self.client.get(reverse('refuge:pet_update', args=[pet.id]))
        self.assertEqual(response.context['object'], pet)
        self.assertEqual(len(response.context['formset']), 4)

    def test_update_pet_invalid_data_has_permission(self):
        vaccine = Vaccine(name='popocha')
        vaccine.save()
        pet = Pet(name='perro cualquiera', sex='hembra', age='2',
                  created_by=self.user, rescue_date='2018-1-3')
        pet.save()
        pet.vaccine.add(vaccine)
        response = self.client.post(reverse('refuge:pet_update', args=[pet.id]),
                                    dict({'name': '', 'sex': 'macho',
                                          'age': 3, 'vaccine': vaccine.id,
                                          'rescue_date': '2018-1-1'},
                                         **data_pet_caract), follow=True)

        self.assertEqual(
            response.request['PATH_INFO'], f'/pet/update/{pet.id}/')
        self.assertEqual(Pet.objects.first().name, 'perro cualquiera')
        self.assertTrue(PetCharacteristic.objects.count() == 0)
        response = self.client.get(reverse('refuge:pet_update', args=[pet.id]))
        self.assertEqual(response.context['object'], pet)
        self.assertEqual(len(response.context['formset']), 3)

    def test_update_pet_valid_data_has_permission_has_not_login(self):
        self.client.logout()
        vaccine = Vaccine(name='popocha')
        vaccine.save()
        pet = Pet(name='perro cualquiera', sex='hembra', age='2',
                  created_by=self.user, rescue_date='2018-1-3')
        pet.save()
        pet.vaccine.add(vaccine)

        response = self.client.post(reverse('refuge:pet_update', args=[pet.id]),
                                    dict({'name': 'mayonesa',
                                          'sex': 'macho', 'age': 3, 'vaccine': vaccine.id,
                                          'rescue_date': '2018-1-1'},
                                         **data_pet_caract), follow=True)

        self.assertEqual(response.request['PATH_INFO'], '/accounts/login/')
        self.assertEqual(Pet.objects.first(), pet)
        self.assertTrue(PetCharacteristic.objects.count() == 0)
        response = self.client.get(reverse('refuge:pet_update', args=[pet.id]))
        self.assertEqual(response.context['object'], pet)
        self.assertEqual(len(response.context['formset']), 3)

    def test_update_pet_valid_data_has_not_permissions(self):
        vaccine = Vaccine(name='popocha')
        vaccine.save()
        vaccine1 = Vaccine(name='zarna')
        vaccine1.save()
        pet = Pet(name='perro cualquiera', sex='hembra', age='2',
                  created_by=self.user, rescue_date='2018-1-3')
        pet.save()
        pet.vaccine.add(vaccine)

        self.client.logout()
        u = User(username='ricardo')
        u.set_password('me vale1234')
        u.save()
        self.user = u
        self.client.force_login(u)
        data = {'name': 'mayonesa', 'sex': 'macho', 'age': 3,
                'vaccine': vaccine1.id,
                'rescue_date': '2018-1-1'}

        self.client.post(reverse('refuge:pet_update',
                                 args=[pet.id]), dict(data, **data_pet_caract), follow=True)

        pet_qs = Pet.objects.first()
        attri = ['name', 'sex', 'age', 'vaccine']
        value = ['perro cualquiera', 'hembra', 2, vaccine]

        for a, v in zip(attri, value):
            if 'vaccine' == a:
                self.assertEqual(pet_qs.vaccine.first(), v)
            else:
                self.assertEqual((getattr(pet_qs, a)), v)
        self.assertTrue(PetCharacteristic.objects.count() == 0)


class AdoptionUpdateViewTest(BaseTestWithLoginMixin, TestCase):

    def test_update_adoption_data_has_permissions(self):
        data_person = {'name': 'marisol', 'last_name': 'playas', 'age': 32,
                       'phone': '498u293842', 'email': 'iefihewi@gamil.com',
                       'home': 'calle del pozo'}

        person = Person(**data_person)
        person.save()
        adoption = AdoptionApplication(person=person,
                                       reasons='por q si solo dame mi maldito perro',
                                       created_by=self.user)
        adoption.save()

        data_pet = {'name': 'michi', 'sex': 'macho', 'created_by': self.user,
                    'age': 2, 'rescue_date': timezone.now(), 'person': person}
        pet = Pet(**data_pet)
        pet.save()

        data_pet2 = {'name': 'koko', 'sex': 'macho', 'created_by': self.user,
                     'age': 2, 'rescue_date': timezone.now()}

        pet2 = Pet(**data_pet2)
        pet2.save()

        data_pet3 = {'name': 'la negra', 'sex': 'hembra', 'created_by': self.user,
                     'age': 2, 'rescue_date': timezone.now()}
        pet3 = Pet(**data_pet3)
        pet3.save()

        data_adoption = {'reasons': 'por que si'}
        data_person2 = {'name': 'marisol', 'last_name': 'playas', 'age': 32,
                        'phone': '99999', 'email': 'iefihewi@gamil1.com',
                        'home': 'calle del pozo'}

        response = self.client.get(
            reverse('refuge:adoption_update', args=[adoption.id]))
        self.assertEqual(response.context['object'], adoption)
        # actualizando datos de la persona
        response = self.client.post(reverse('refuge:adoption_update', args=[adoption.id]),
                                    dict({'pets': [pet2.id]}, **data_person2,
                                         **data_adoption), follow=True)
        self.assertEqual(
            response.request['PATH_INFO'], f'/pet/adoption/list/')

        pet = Pet.objects.get(id=pet.id)
        pet2 = Pet.objects.get(id=pet2.id)
        self.assertEqual(pet.person, person)
        person = Person.objects.get()
        self.assertTrue(pet2.person == person)
        for key, value in data_person2.items():
            self.assertEqual(getattr(person, key), value)
        dict(data_adoption, **{'person': person})
        adoption = AdoptionApplication.objects.get()
        for attri, value in data_adoption.items():
            self.assertEqual(getattr(adoption, attri), value)

        # validando actualizacion sin seleccionar ninguna mascota

        response = self.client.post(reverse('refuge:adoption_update', args=[adoption.id]),
                                    dict({'pets': []}, **data_person, **data_adoption),
                                    follow=True)

        self.assertEqual(response.request['PATH_INFO'], f'/pet/adoption/update/{adoption.id}/')

        adoption = AdoptionApplication.objects.get()
        self.assertEqual(pet.person, person)
        person = Person.objects.get()
        self.assertTrue(pet2.person == person)
        for key, value in data_person2.items():
            self.assertEqual(getattr(person, key), value)
        for attri, value in data_adoption.items():
            self.assertEqual(getattr(adoption, attri), value)
        response = self.client.get(
            reverse('refuge:adoption_update', args=[adoption.id]))
        self.assertEqual(response.context['object'], adoption)
        # seleccionando una mascota
        response = self.client.post(reverse('refuge:adoption_update', args=[adoption.id]),
                                    dict({'pets': [pet.id]}, **data_person2, **data_adoption),
                                    follow=True)
        self.assertEqual(
            response.request['PATH_INFO'], f'/pet/adoption/list/')
        adoption = AdoptionApplication.objects.get()

        self.assertEqual(pet.person, person)
        person = Person.objects.get()
        self.assertTrue(pet2.person == person)

        for key, value in data_person2.items():
            self.assertEqual(getattr(person, key), value)
        for attri, value in data_adoption.items():
            self.assertEqual(getattr(adoption, attri), value)
        pet = Pet.objects.get(id=pet.id)
        self.assertEqual(pet.person, person)
        pet.person = None
        pet.save()
        # seleccionando 2 mascotas
        response = self.client.post(reverse('refuge:adoption_update', args=[adoption.id]),
                                    dict({'pets': [pet.id, pet2.id]}, **data_person,
                                         **data_adoption), follow=True)

        self.assertEqual(
            response.request['PATH_INFO'], f'/pet/adoption/list/')
        pet = Pet.objects.get(id=pet.id)
        pet2 = Pet.objects.get(id=pet2.id)

        self.assertEqual(pet.person, person)
        self.assertEqual(pet2.person, person)
        # validando que en una actualizacion no se puede seleccionar una mascota ya tomada por una persona diferente

        data_person2 = {'name': 'jorge', 'last_name': 'playas', 'age': 32,
                        'phone': '498u293842', 'email': 'jorge@gamil.com',
                        'home': 'calle del pozo'}

        person2 = Person(**data_person2)
        person2.save()
        adoption2 = AdoptionApplication(person=person2,
                                        reasons='por q si solo dame mi maldito perro',
                                        created_by=self.user)
        adoption2.save()
        response = self.client.post(reverse('refuge:adoption_update', args=[adoption2.id]),
                                    dict({'pets': [pet.id, pet3.id]}, **data_person2,
                                         **data_adoption),
                                    follow=True)
        self.assertEqual(response.request['PATH_INFO'],
                         f'/pet/adoption/update/{adoption2.id}/')
        pet = Pet.objects.get(id=pet.id)
        pet3 = Pet.objects.get(id=pet3.id)

        self.assertEqual(pet.person, person)
        self.assertTrue(pet3.person is None)

    def test_update_adoption_invalid_data_has_permission(self):

        person = Person(name='carlos', last_name='xoxo', age='23',
                        email='coaa@gmai.com', home='calle brava')
        person.save()
        adoption = AdoptionApplication(person=person,
                                       reasons='por q si solo dame mi maldito perro',
                                       created_by=self.user)
        adoption.save()

        self.client.post(reverse('refuge:adoption_update', args=[adoption.id]),
                         {'name': 'ertfyg', 'last_name': 'playas', 'age': 'b',
                          'phone': '498293842', 'email': 'xfxfxdf',
                          'home': 'calle del pozo',
                          'reasons': ''}, follow=True)

        self.assertEqual(AdoptionApplication.objects.first().person, person)
        self.assertEqual(AdoptionApplication.objects.first().reasons,
                         'por q si solo dame mi maldito perro')
        response = self.client.get(
            reverse('refuge:adoption_update', args=[adoption.id]))
        self.assertEqual(response.context['object'], adoption)

    def test_update_adoption_valid_data_has_not_login(self):

        person = Person(name='carlos', last_name='xoxo', age='23',
                        email='coaa@gmai.com', home='calle brava')
        person.save()
        adoption = AdoptionApplication(person=person,
                                       reasons='por q si solo dame mi maldito perro',
                                       created_by=self.user)
        adoption.save()
        self.client.logout()
        data = {'name': 'marisol', 'last_name': 'playas', 'age': '35',
                'phone': '498u293842', 'email': 'iefihewi@gamil.com',
                'home': 'calle del pozo',
                'reasons': 'por que si'}

        response = self.client.post(reverse('refuge:adoption_update',
                                            args=[adoption.id]), data, follow=True)
        adoption_qs = AdoptionApplication.objects.first()

        self.assertEquals(response.request['PATH_INFO'], '/accounts/login/')
        self.assertEquals(adoption_qs.person, person)
        self.assertEquals(adoption_qs, adoption)

    def test_update_adoption_valid_data_has_login_has_not_permissions(self):

        person = Person(name='carlos', last_name='xoxo', age='23',
                        email='coaa@gmai.com', home='calle brava')
        person.save()
        adoption = AdoptionApplication(person=person,
                                       reasons='por q si solo dame mi maldito perro',
                                       created_by=self.user)
        adoption.save()
        self.client.logout()
        u = User(username='ricardo')
        u.set_password('me vale1234')
        u.save()
        self.user = u
        self.client.force_login(u)
        data = {'name': 'marisol', 'last_name': 'playas', 'age': '35',
                'phone': '498u293842', 'email': 'iefihewi@gamil.com',
                'home': 'calle del pozo',
                'reasons': 'por que si'}
        response = self.client.get(
            reverse('refuge:adoption_update', args=[adoption.id]))
        self.assertEqual(response.context['object'], adoption)

        response = self.client.post(reverse('refuge:adoption_update',
                                            args=[adoption.id]), data, follow=True)
        adoption_qs = AdoptionApplication.objects.first()

        self.assertEquals(response.request['PATH_INFO'], '/accounts/login/')
        self.assertEquals(adoption_qs.person, person)
        self.assertEquals(adoption_qs, adoption)


class PetDeleteViewTest(BaseTestWithLoginMixin, TestCase):

    def test_delete_pet_has_permissions(self):
        vaccine = Vaccine(name='prueba')
        vaccine.save()
        pet = Pet(name='perro', sex='hembra', age='2',
                  created_by=self.user, rescue_date=timezone.now())
        pet.save()
        pet.vaccine.add(vaccine)
        response = self.client.post(
            reverse('refuge:pet_delete', args=[pet.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('refuge:pet_list'))
        self.assertIs(Pet.objects.first(), None)

    def test_delete_pet_has_not_login(self):
        self.client.logout()
        vaccine = Vaccine(name='prueba')
        vaccine.save()
        pet = Pet(name='perro', sex='hembra', age='2',
                  created_by=self.user, rescue_date=timezone.now())
        pet.save()
        pet.vaccine.add(vaccine)
        response = self.client.post(
            reverse('refuge:pet_delete', args=[pet.id]), follow=True)
        self.assertEqual(response.request['PATH_INFO'], '/accounts/login/')
        self.assertEqual(Pet.objects.first(), pet)

    def test_delete_pet_has_not_permissions_has_login(self):

        vaccine = Vaccine(name='prueba')
        vaccine.save()
        pet = Pet(name='perro', sex='hembra', age='2',
                  created_by=self.user, rescue_date=timezone.now())
        pet.save()
        pet.vaccine.add(vaccine)
        self.client.logout()
        u = User(username='ricardo')
        u.set_password('me vale1234')
        u.save()
        self.user = u
        self.client.force_login(u)
        response = self.client.post(
            reverse('refuge:pet_delete', args=[pet.id]), follow=True)
        self.assertEqual(response.request['PATH_INFO'], '/accounts/login/')
        self.assertEqual(Pet.objects.first(), pet)


class AdoptionDeleteViewTest(BaseTestWithLoginMixin, TestCase):

    def test_delete_adoption_has_permissions(self):
        person = Person(name='carlos', last_name='xoxo', age='23',
                        email='coaa@gmai.com', home='calle brava')
        person.save()
        adoption = AdoptionApplication(person=person, reasons='por q si',
                                       created_by=self.user)
        adoption.save()

        response = self.client.post(
            reverse('refuge:adoption_delete', args=[adoption.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('refuge:adoption_list'))
        self.assertTrue(AdoptionApplication.objects.first() is None)

    def test_delete_adoption_has_not_login(self):
        self.client.logout()
        person = Person(name='carlos', last_name='xoxo', age='23',
                        email='coaa@gmai.com', home='calle brava')
        person.save()
        adoption = AdoptionApplication(person=person, reasons='por q si',
                                       created_by=self.user)
        adoption.save()

        response = self.client.post(
            reverse('refuge:adoption_delete', args=[adoption.id]), follow=True)

        self.assertEqual(response.request['PATH_INFO'], '/accounts/login/')
        self.assertEqual(AdoptionApplication.objects.first(), adoption)

    def test_delete_adoption_has_login_has_not_permissions(self):

        person = Person(name='carlos', last_name='xoxo', age='23',
                        email='coaa@gmai.com', home='calle brava')
        person.save()
        adoption = AdoptionApplication(person=person, reasons='por q si',
                                       created_by=self.user)
        adoption.save()
        self.client.logout()
        u = User(username='ricardo')
        u.set_password('me vale1234')
        u.save()
        self.user = u
        self.client.force_login(u)
        response = self.client.post(
            reverse('refuge:adoption_delete', args=[adoption.id]), follow=True)

        self.assertEqual(response.request['PATH_INFO'], '/accounts/login/')
        self.assertEqual(AdoptionApplication.objects.first(), adoption)


class PetListViewTest(BaseTestWithLoginMixin, TestCase):

    def test_load_pet_objects_has_permissions(self):

        vaccine = Vaccine(name='prueba')
        vaccine.save()
        pet = Pet(name='perro', sex='hembra', age='2',
                  created_by=self.user, rescue_date=timezone.now())
        pet.save()
        response = self.client.get(reverse('refuge:pet_list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['object_list'],
            ['<Pet: perro>']
        )

    def test_load_pet_objects_has_not_login(self):

        vaccine = Vaccine(name='prueba')
        vaccine.save()
        person = Person(name='carlos', last_name='xoxo', age='23',
                        email='coaa@gmai.com', home='calle brava')
        person.save()
        pet = Pet(name='perro', sex='hembra', age='2',
                  created_by=self.user, rescue_date=timezone.now())
        pet.save()
        self.client.logout()
        response = self.client.get(reverse('refuge:pet_list'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/accounts/login/?next=/pet/list/')


class AdoptionListViewTest(BaseTestWithLoginMixin, TestCase):

    def test_load_adoption_objects_has_permissions(self):

        person = Person(name='carlos', last_name='xoxo', age='23',
                        email='coaa@gmai.com', home='calle brava')
        person.save()
        adoption = AdoptionApplication(person=person,
                                       reasons='por q si', created_by=self.user)
        adoption.save()
        response = self.client.get(reverse('refuge:adoption_list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['object_list'],
            ['<AdoptionApplication: por q si>']
        )

    def test_load_adoption_objects_has_not_login(self):

        person = Person(name='carlos', last_name='xoxo', age='23',
                        email='coaa@gmai.com', home='calle brava')
        person.save()
        adoption = AdoptionApplication(person=person,
                                       reasons='por q si', created_by=self.user)
        adoption.save()
        self.client.logout()
        response = self.client.get(reverse('refuge:adoption_list'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, '/accounts/login/?next=/pet/adoption/list/')
