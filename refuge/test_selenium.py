from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from .models import Pet, AdoptionApplication, Vaccine, Person
from django.contrib.auth.models import User
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import os
import binascii
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from django.test import LiveServerTestCase


class BaseTestMixin(object):

    def generete_name(self):
        return binascii.hexlify(os.urandom(5)).decode('ascii')

    def create_vaccine(self):
        vaccine = Vaccine(name=self.generete_name())
        vaccine.save()
        return vaccine

    def create_person(self):
        person = Person(name=self.generete_name(), last_name='robles', age='23',
                        email='coaa@gmai.com', home='calle brava', phone='95112345')
        person.save()
        return person

    def create_pet(self, person, vaccine):
        pet = Pet(name='perro cualquiera', person=person, sex='hembra', age='2',
                  created_by=self.user, rescue_date='2018-1-1')
        pet.save()
        pet.vaccine.add(vaccine)
        return pet

    def create_adoption_app(self, person):

        adoption = AdoptionApplication(person=person, number_pets='1',
                                       reasons='por que quiero una mascota',
                                       created_by=self.user)
        adoption.save()
        return adoption


class LoginMixin(object):

    def wait(self, delay, element):
        try:
            myElem = WebDriverWait(self.selenium, delay).until(
                EC.presence_of_element_located((By.NAME, element)))

        except TimeoutException:
            print('Loading took too much time!')
        return myElem

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='usuario',
            password='usuario'
        )
        self.user.is_active = True
        self.user.save()
        self.selenium = WebDriver()
        self.selenium.implicitly_wait(10)
        self.selenium.get(f'{self.live_server_url}/')
        username = self.selenium.find_element_by_name('username')
        username.send_keys('usuario')
        password = self.selenium.find_element_by_name('password')
        password.send_keys('usuario')
        self.selenium.find_element_by_name('login').click()

    def tearDown(self):
        self.selenium.quit()
        super().tearDown()


class PetTestCreateViewTest(LoginMixin, BaseTestMixin, LiveServerTestCase):

    def test_create_pet_valid_data_has_login(self):
        vaccine = [self.create_vaccine(), self.create_vaccine()]
        person = self.create_person()
        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/pet/create/')
        self.assertEquals('Form', selenium.title)
        selenium.('name').send_keys('cachoro')
        Select(selenium.find_element_by_name('person')).select_by_index(1)
        selenium.find_element_by_name('sex').send_keys('macho')
        selenium.find_element_by_name('age').send_keys('2')
        vaccineItem = selenium.find_element_by_name('vaccine')
        selenium.find_element_by_name('rescue_date').send_keys('2018-1-2')
        submit = selenium.find_element_by_name('save')

        select = Select(vaccineItem)
        all_options = [o.get_attribute('value') for o in select.options]
        for x in all_options:
            select.select_by_value(x)

        submit.send_keys(Keys.RETURN)
        self.wait(5, 'edit')
        self.assertEquals('Pet List', selenium.title)

        pet = Pet.objects.first()
        ATTRI = ['name', 'person', 'vaccine', 'sex', 'age']
        VALUE = ['cachoro', person, '', 'macho', 2]

        for a, v in zip(ATTRI, VALUE):
            if a == 'vaccine':
                for va, va1 in zip(vaccine, pet.vaccine.all()):
                    self.assertEqual(va, va1)
            else:
                self.assertEqual(getattr(pet, a), v)

    def test_creat_invalid_data_has_login(self):
        self.create_vaccine()
        self.create_vaccine()
        self.create_person()
        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/pet/create/')
        self.assertEquals('Form', selenium.title)
        selenium.find_element_by_name('name').send_keys('')
        Select(selenium.find_element_by_name('person')).select_by_index(1)
        selenium.find_element_by_name('sex').send_keys('macho')
        selenium.find_element_by_name('age').send_keys('nnkj')
        vaccineItem = selenium.find_element_by_name('vaccine')
        selenium.find_element_by_name('rescue_date').send_keys('2018-13-2')
        submit = selenium.find_element_by_name('save')

        select = Select(vaccineItem)
        all_options = [o.get_attribute('value') for o in select.options]
        for x in all_options:
            select.select_by_value(x)

        submit.send_keys(Keys.RETURN)
        self.wait(5, 'save')
        self.assertEquals('Form', selenium.title)
        self.assertTrue(Pet.objects.first(), None)


class PetTestDeleteViewTest(LoginMixin, BaseTestMixin, LiveServerTestCase):

    def test_delete_pet_has_login(self):

        pet = self.create_pet(self.create_person(), self.create_vaccine())

        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/pet/delete/{pet.id}')
        self.wait(5, 'delete').send_keys(Keys.RETURN)
        self.wait(5, 'table')
        self.assertEquals('Pet List', selenium.title)
        self.assertIs(Pet.objects.first(), None)


class PetTestListViewTest(LoginMixin, BaseTestMixin, LiveServerTestCase):

    def test_objects_pet_has_login(self):
        self.create_pet(self.create_person(), self.create_vaccine())
        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/pet/list/')
        self.wait(5, 'delete').send_keys(Keys.RETURN)
        self.wait(5, 'cancel').send_keys(Keys.RETURN)
        self.wait(5, 'edit').send_keys(Keys.RETURN)
        self.wait(5, 'data-form')
        self.assertEquals('Form', selenium.title)


class PetTestUpdateViewTest(LoginMixin, BaseTestMixin, LiveServerTestCase):

    def test_update_data_with_permissions(self):

        person = self.create_person()
        pet = self.create_pet(self.create_person(), self.create_vaccine())
        vaccine = self.create_vaccine()
        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/pet/update/{pet.id}')
        self.wait(5, 'data-form')

        name = selenium.find_element_by_name('name')
        name.clear()
        name.send_keys('cachoro')
        Select(selenium.find_element_by_name('person')).select_by_index(1)
        sex = selenium.find_element_by_name('sex')
        sex.clear()
        sex.send_keys('hembra')
        age = selenium.find_element_by_name('age')
        age.clear()
        age.send_keys('5')
        vaccineItem = selenium.find_element_by_name('vaccine')
        date = selenium.find_element_by_name('rescue_date')
        date.clear()
        date.send_keys('2017-1-1')
        select = Select(vaccineItem)
        select.select_by_index(0)
        select.select_by_visible_text(vaccine.name)

        selenium.find_element_by_name('save').send_keys(Keys.RETURN)
        self.wait(5, 'edit')
        self.assertEquals('Pet List', selenium.title)

        pet = Pet.objects.first()
        ATTRI = ['name', 'sex', 'age', 'person', 'vaccine']
        VALUE = ['cachoro', 'hembra', 5, person, vaccine]

        for a, v in zip(ATTRI, VALUE):
            if a == 'vaccine':
                self.assertEqual(pet.vaccine.get(id=vaccine.id), v)
            else:
                self.assertEqual(getattr(pet, a), v)


class AdoptionTestCreateViewTest(LoginMixin, BaseTestMixin, LiveServerTestCase):

    def test_adoption_data_is_valid(self):
        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/pet/adoption/create/')
        self.assertEquals('Form', selenium.title)

        selenium.find_element_by_name('name').send_keys('marisol')
        selenium.find_element_by_name('last_name').send_keys('playas')
        selenium.find_element_by_name('age').send_keys('35')
        selenium.find_element_by_name('phone').send_keys('87654321')
        selenium.find_element_by_name('email').send_keys('cosas@gmail.com')
        selenium.find_element_by_name('home').send_keys('calle del rio')
        selenium.find_element_by_name('number_pets').send_keys('3')
        selenium.find_element_by_name(
            'reasons').send_keys('quiero una mascota')
        selenium.find_element_by_name('save').send_keys(Keys.RETURN)
        self.wait(5, 'edit')
        self.assertEquals('Adoption List', selenium.title)

        ATTRIPEOPLE = ['name', 'last_name', 'age', 'phone',
                       'email', 'home']
        ATTRI = ['person', 'number_pets', 'reasons']

        VALUEPEOPLE = ['marisol', 'playas', 35, '87654321',
                       'cosas@gmail.com', 'calle del rio']
        VALUE = ['', 3, 'quiero una mascota']
        adoption = AdoptionApplication.objects.first()

        for a, v in zip(ATTRI, VALUE):
            if a == 'person':
                for ap, vp in zip(ATTRIPEOPLE, VALUEPEOPLE):
                    self.assertEqual(getattr(adoption.person, ap), vp)
            else:
                self.assertEqual(getattr(adoption, a), v)


class AdoptionTestDeleteViewTest(LoginMixin, BaseTestMixin, LiveServerTestCase):

    def test_delete_data_with_permissions(self):

        adoption = self.create_adoption_app(self.create_person())
        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/pet/adoption/delete/{adoption.id}')
        self.wait(5, 'delete').send_keys(Keys.RETURN)
        self.wait(5, 'table')
        self.assertEquals('Adoption List', selenium.title)
        self.assertIs(AdoptionApplication.objects.first(), None)


class AdoptionTestListViewTest(LoginMixin, BaseTestMixin, LiveServerTestCase):

    def test_existing_objects_adoption(self):

        self.create_adoption_app(self.create_person())
        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/pet/adoption/list/')
        self.wait(5, 'table')
        self.assertEquals('Adoption List', selenium.title)
        self.wait(5, 'delete').send_keys(Keys.RETURN)
        self.wait(5, 'cancel').send_keys(Keys.RETURN)
        self.wait(5, 'edit').send_keys(Keys.RETURN)
        self.wait(5, 'data-form')
        self.assertEquals('Form', selenium.title)


class AdoptionTestUpdateViewTest(LoginMixin, BaseTestMixin, LiveServerTestCase):

    def test_update_data_with_permissions(self):
        self.create_vaccine()
        adoption = self.create_adoption_app(
            self.create_person())

        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/pet/adoption/update/{adoption.id}')
        self.wait(5, 'data-form')
        self.assertEquals('Form', selenium.title)

        name = selenium.find_element_by_name('name')
        name.clear()
        name.send_keys('marisol')
        last_name = selenium.find_element_by_name('last_name')
        last_name.clear()
        last_name.send_keys('playas')
        age = selenium.find_element_by_name('age')
        age.clear()
        age.send_keys('35')
        phone = selenium.find_element_by_name('phone')
        phone.clear()
        phone.send_keys('87654321')
        email = selenium.find_element_by_name('email')
        email.clear()
        email.send_keys('cosas@gmail.com')
        home = selenium.find_element_by_name('home')
        home.clear()
        home.send_keys('calle del rio')
        number_pets = selenium.find_element_by_name('number_pets')
        number_pets.clear()
        number_pets.send_keys('10')
        reasons = selenium.find_element_by_name('reasons')
        reasons.clear()
        reasons.send_keys('quiero una mascota')
        selenium.find_element_by_name('save').send_keys(Keys.RETURN)

        self.wait(5, 'table')
        self.assertEquals('Adoption List', selenium.title)
        ATTRIPEOPLE = ['name', 'last_name', 'age', 'phone',
                       'email', 'home']
        ATTRI = ['person', 'number_pets', 'reasons']

        VALUEPEOPLE = ['marisol', 'playas', 35, '87654321',
                       'cosas@gmail.com', 'calle del rio']
        VALUE = ['', 10, 'quiero una mascota']
        adoption = AdoptionApplication.objects.first()

        for a, v in zip(ATTRI, VALUE):
            if a == 'person':
                for ap, vp in zip(ATTRIPEOPLE, VALUEPEOPLE):
                    self.assertEqual(getattr(adoption.person, ap), vp)
            else:
                self.assertEqual(getattr(adoption, a), v)


class LoginOutTestViewTest(LoginMixin, BaseTestMixin, LiveServerTestCase):

    def test_user_can_close_session(self):

        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/pet/')
        self.wait(5, 'loginOut')
        self.assertEquals('Welcome', selenium.title)
        selenium.find_element_by_link_text('opciones').click()
        selenium.find_element_by_link_text('Salir').click()
        self.wait(5, 'login-form')
        self.assertEquals('Login', selenium.title)
