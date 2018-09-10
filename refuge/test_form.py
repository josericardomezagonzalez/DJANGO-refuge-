from django.contrib.auth.models import User
from django.test import Client, TestCase
from .models import Person, Vaccine, Pet
from .forms import PetForm, AdoptionForm, PersonForm, PetCharacteristicFormSet


class PetCharacteristicFormSetTest(TestCase):
    def setUp(self):
        self.client = Client()
        u = User(username="claustofo")
        u.set_password('love rock and matal and more')
        u.save()
        self.user = u
        self.client.force_login(u)

    def test_is_valid_and_save(self):
        vaccine = Vaccine(name="prueba")
        vaccine.save()
        vaccine1 = Vaccine(name="zarna")
        vaccine1.save()
        data_pet = {'name': "totuga ninja",
                    'sex': "macho",
                    'age': 2,
                    'rescue_date': "2018-12-1",
                    'created_by': self.user
                    }

        pet = Pet(**data_pet)
        pet.save()
        pet.vaccine.add(vaccine)
        pet.vaccine.add(vaccine1)
        data = {'petcharacteristic_set-TOTAL_FORMS': '3',
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
        pet_charac_formset = PetCharacteristicFormSet(data)
        self.assertTrue(pet_charac_formset.is_valid())
        pet_charac_formset.instance = pet
        pet_charac_list = pet_charac_formset.save()
        self.assertTrue(pet_charac_list == [])

        data = {'petcharacteristic_set-TOTAL_FORMS': '3',
                'petcharacteristic_set-INITIAL_FORMS': '0',
                'petcharacteristic_set-MIN_NUM_FORMS': '0',
                'petcharacteristic_set-MAX_NUM_FORMS': '1000',
                'petcharacteristic_set-0-key': 'color de pelo',
                'petcharacteristic_set-0-value': 'sin pelo',
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

        pet_charac_formset = PetCharacteristicFormSet(data)
        self.assertTrue(pet_charac_formset.is_valid())
        pet_charac_formset.instance = pet
        pet_charac_list = pet_charac_formset.save()
        self.assertEqual(pet_charac_list[0].key, 'color de pelo')
        self.assertEqual(pet_charac_list[0].value, 'sin pelo')

        data = {'petcharacteristic_set-TOTAL_FORMS': '3',
                'petcharacteristic_set-INITIAL_FORMS': '0',
                'petcharacteristic_set-MIN_NUM_FORMS': '0',
                'petcharacteristic_set-MAX_NUM_FORMS': '1000',
                'petcharacteristic_set-0-key': 'cola',
                'petcharacteristic_set-0-value': 'rota',
                'petcharacteristic_set-0-id': '',
                'petcharacteristic_set-0-pet': '',
                'petcharacteristic_set-1-key': 'tamaño',
                'petcharacteristic_set-1-value': 'muy alto',
                'petcharacteristic_set-1-id': '',
                'petcharacteristic_set-1-pet': '',
                'petcharacteristic_set-2-key': '',
                'petcharacteristic_set-2-value': '',
                'petcharacteristic_set-2-id': '',
                'petcharacteristic_set-2-pet': '',
                }

        pet_charac_formset = PetCharacteristicFormSet(data)
        self.assertTrue(pet_charac_formset.is_valid())
        pet_charac_formset.instance = pet
        pet_charac_list = pet_charac_formset.save()
        self.assertEqual(pet_charac_list[0].key, 'cola')
        self.assertEqual(pet_charac_list[0].value, 'rota')
        self.assertEqual(pet_charac_list[1].key, 'tamaño')
        self.assertEqual(pet_charac_list[1].value, 'muy alto')


class PetFormTest(TestCase):

    def setUp(self):
        self.client = Client()
        u = User(username="claustofo")
        u.set_password('love rock and matal and more')
        u.save()
        self.user = u
        self.client.force_login(u)

    def test_is_valid_and_save(self):
        vaccine = Vaccine(name="prueba")
        vaccine.save()
        vaccine1 = Vaccine(name="zarna")
        vaccine1.save()
        person = Person(name="carlos", last_name="xoxo", age="23",
                        email="coaa@gmail.com", home="calle brava")
        person.save()
        data = {'name': "totuga ninja",
                'person': person.id,
                'vaccine': [vaccine.id, vaccine1.id],
                'sex': "macho",
                'age': 2,
                'rescue_date': "2018-12-1"
                }
        form = PetForm(data=data, user=self.user)

        self.assertTrue(form.is_valid())
        pet = form.save()
        data.pop('rescue_date')

        for attri, value in data.items():
            if attri == "vaccine":
                for v, p in zip(value, pet.vaccine.all()):
                    self.assertEqual(v, p.id)
            elif attri == "person":
                self.assertEqual(value, person.id)
            else:
                self.assertEqual(getattr(pet, attri), value)

    def test_is_invalid(self):
        vaccine = Vaccine(name="prueba")
        vaccine.save()
        person = Person(name="carlos", last_name="xoxo", age="3",
                        email="coaa@gmail.com", home="calle brava")
        person.save()
        data = {'name': "totuga ninja",
                'person': person.id,
                'vaccine': [vaccine.id],
                'sex': "macho",
                'age': "as",
                'rescue_date': "2018-12-32"
                }
        form = PetForm(data=data, user=self.user)

        self.assertIs(form.is_valid(), False)


class PersonFormTest(TestCase):

    def setUp(self):
        self.client = Client()
        u = User(username="claustofo")
        u.set_password('love rock and matal and more')
        u.save()
        self.user = u
        self.client.force_login(u)

    def test_is_valid(self):
        data = {'name': "chango feo", 'last_name': "ravioli",
                'age': 100, 'phone': "987654321",
                'email': "coaa@gmail.com", 'home': "la chintrola"}

        form = PersonForm(data=data)
        self.assertIs(form.is_valid(), True)
        form.save(commit=True)
        person = Person.objects.get()

        for attri, value in data.items():
            self.assertEqual(getattr(person, attri), value)

    def test_is_not_valid(self):
        form = PersonForm(data={
            'name': "",
            'last_name': "ravioli",
            'age': "100",
            'phone': "987654321",
            'email': "coaa@gmail.com",
            'home': "la chintrola"
        })
        self.assertIs(form.is_valid(), False)


class AdoptionFormTest(TestCase):

    def setUp(self):
        self.client = Client()
        u = User(username="claustofo")
        u.set_password('love rock and matal and more')
        u.save()
        self.user = u
        self.client.force_login(u)

    def test_is_valid_and_save(self):
        vaccine = Vaccine(name="prueba")
        vaccine.save()
        vaccine1 = Vaccine(name="zarna")
        vaccine1.save()
        data_pet = {'name': "totuga ninja",
                    'sex': "macho",
                    'age': 2,
                    'rescue_date': "2018-12-1",
                    'created_by': self.user
                    }

        pet = Pet(**data_pet)
        pet.save()
        pet.vaccine.add(vaccine)
        pet.vaccine.add(vaccine1)

        datap = {'name': 'marisol', 'last_name': 'playas', 'age': '35', 'phone': '498u293842',
                 'email': 'iefihewi@gamil.com', 'home': 'calle del pozo'}

        form = PersonForm(data=datap)
        self.assertIs(form.is_valid(), True)
        form.save(commit=True)
        person = Person.objects.get()

        data = {'number_pets': "2", 'reasons': "lo que sea", 'pets': [pet.id]}

        form1 = AdoptionForm(data=data, user=self.user, person=person)
        self.assertIs(form1.is_valid(), True)
        form1.save(commit=True)
        pet = Pet.objects.get()
        self.assertEquals(pet.person, person)

    def test_is_not_valid(self):

        form_data = {'number_pets': "", 'reasons': "lo que sea", 'name': 'marisol',
                     'last_name': 'playas', 'age': '35', 'phone': '498u293842',
                     'email': 'iefihewi', 'home': 'calle del pozo'}

        form = AdoptionForm(data=form_data, user=self.user)
        self.assertIs(form.is_valid(), False)
