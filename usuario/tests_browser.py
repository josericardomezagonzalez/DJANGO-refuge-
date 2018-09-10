from django.contrib.auth.models import User
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import os
import binascii
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
import time
import unittest


class BaseMixin(object):

    def select_element_by_name_wait(self, selenium, delay, element):
        try:
            myElem = WebDriverWait(selenium, delay).until(
                EC.presence_of_element_located((By.NAME, element)))

        except TimeoutException:
            print('Loading took too much time!')
        return myElem

    def select_element_by_class_name(self, selenium, delay, element):
        try:
            myElem = WebDriverWait(selenium, delay).until(
                EC.presence_of_element_located((By.CLASS_NAME, element)))

        except TimeoutException:
            print('Loading took too much time!')
        return myElem


class CustomLoginViewTest(BaseMixin, StaticLiveServerTestCase):
    port = 8000

    def setUp(self):
        super().setUp()

    def tearDown(self):
        self.selenium.quit()
        self.selenium2.quit()
        super().tearDown()

    def login_with_a_successful_session(self):
        self.user = User.objects.create_user(
            username='usuario',
            password='usuario'
        )
        self.user.is_active = True
        self.user.save()
        self.selenium = webdriver.Firefox()
        selenium = self.selenium
        selenium.implicitly_wait(10)
        selenium.get(f'{self.live_server_url}/')
        username = selenium.find_element_by_name('username')
        username.send_keys('usuario')
        password = selenium.find_element_by_name('password')
        password.send_keys('usuario')
        selenium.find_element_by_name('login').click()
        self.select_element_by_name_wait(selenium, 5, 'loginOut')
        self.assertEquals('Welcome', selenium.title)

    def log_in_two_successful_sessions(self):

        self.user = User.objects.create_user(
            username='usuario',
            password='usuario'
        )
        self.user.is_active = True
        self.user.save()
        self.selenium = webdriver.Firefox()
        selenium = self.selenium
        selenium.implicitly_wait(10)
        selenium.get(f'{self.live_server_url}/')
        username = selenium.find_element_by_name('username')
        username.send_keys('usuario')
        password = selenium.find_element_by_name('password')
        password.send_keys('usuario')
        selenium.find_element_by_name('login').click()
        self.select_element_by_name_wait(selenium, 5, 'loginOut')
        self.assertEquals('Welcome', selenium.title)
        self.selenium2 = webdriver.Firefox()
        selenium2 = self.selenium2
        selenium2.implicitly_wait(10)
        selenium2.get(f'{self.live_server_url}/')
        username = selenium2.find_element_by_name('username')
        username.send_keys('usuario')
        password = selenium2.find_element_by_name('password')
        password.send_keys('usuario')
        selenium2.find_element_by_name('login').click()
        time.sleep(1)
        self.assertEquals('Esperando autorizacion', selenium2.title)
        self.select_element_by_class_name(selenium, 10, 'btn-success').click()
        self.select_element_by_name_wait(selenium2, 5, 'loginOut')
        self.assertEquals('Welcome', selenium.title)
        time.sleep(2)

    def login_with_a_successful_session_and_one_rejected(self):

        self.user = User.objects.create_user(
            username='usuario',
            password='usuario'
        )
        self.user.is_active = True
        self.user.save()
        self.selenium = webdriver.Firefox()
        selenium = self.selenium
        selenium.implicitly_wait(10)
        selenium.get(f'{self.live_server_url}/')
        username = selenium.find_element_by_name('username')
        username.send_keys('usuario')
        password = selenium.find_element_by_name('password')
        password.send_keys('usuario')
        selenium.find_element_by_name('login').click()
        self.select_element_by_name_wait(selenium, 5, 'loginOut')
        self.assertEquals('Welcome', selenium.title)
        self.selenium2 = webdriver.Firefox()
        selenium2 = self.selenium2
        selenium2.implicitly_wait(10)
        selenium2.get(f'{self.live_server_url}/')
        username = selenium2.find_element_by_name('username')
        username.send_keys('usuario')
        password = selenium2.find_element_by_name('password')
        password.send_keys('usuario')
        selenium2.find_element_by_name('login').click()
        time.sleep(1)
        self.assertEquals('Esperando autorizacion', selenium2.title)
        self.select_element_by_class_name(selenium, 10, 'btn-danger').click()
        time.sleep(2)
        self.assertEquals('Sin permisos', selenium2.title)
        time.sleep(2)

    def login_with_two_successful_session_and_one_rejected(self):
        self.user = User.objects.create_user(
            username='usuario',
            password='usuario'
        )
        self.user.is_active = True
        self.user.save()
        self.selenium = webdriver.Firefox()
        selenium = self.selenium
        selenium.implicitly_wait(10)
        selenium.get(f'{self.live_server_url}/')
        username = selenium.find_element_by_name('username')
        username.send_keys('usuario')
        password = selenium.find_element_by_name('password')
        password.send_keys('usuario')
        selenium.find_element_by_name('login').click()
        self.select_element_by_name_wait(selenium, 5, 'loginOut')
        self.assertEquals('Welcome', selenium.title)
        self.selenium2 = webdriver.Firefox()
        selenium2 = self.selenium2
        selenium2.implicitly_wait(10)
        selenium2.get(f'{self.live_server_url}/')
        username = selenium2.find_element_by_name('username')
        username.send_keys('usuario')
        password = selenium2.find_element_by_name('password')
        password.send_keys('usuario')
        selenium2.find_element_by_name('login').click()
        time.sleep(2)
        self.assertEquals('Esperando autorizacion', selenium2.title)
        self.select_element_by_class_name(selenium, 10, 'btn-success').click()
        self.select_element_by_name_wait(selenium2, 10, 'loginOut')
        self.assertEquals('Welcome', selenium2.title)
        time.sleep(2)

        self.selenium3 = webdriver.Firefox()
        selenium3 = self.selenium3
        selenium3.implicitly_wait(10)
        selenium3.get(f'{self.live_server_url}/')
        username = selenium3.find_element_by_name('username')
        username.send_keys('usuario')
        password = selenium3.find_element_by_name('password')
        password.send_keys('usuario')
        selenium3.find_element_by_name('login').click()
        time.sleep(2)
        self.assertEquals('Esperando autorizacion', selenium3.title)
        self.select_element_by_class_name(
            selenium2, 10, 'btn-danger').click()
        time.sleep(2)
        self.assertEquals('Sin permisos', selenium3.title)
        time.sleep(2)
        self.selenium3.quit()

    def login_with_four_successful_session_of_two_different_user(self):
        self.user = User.objects.create_user(
            username='usuario',
            password='usuario'
        )
        self.user.is_active = True
        self.user.save()
        self.selenium = webdriver.Firefox()
        selenium = self.selenium
        selenium.implicitly_wait(10)
        selenium.get(f'{self.live_server_url}/')
        username = selenium.find_element_by_name('username')
        username.send_keys('usuario')
        password = selenium.find_element_by_name('password')
        password.send_keys('usuario')
        selenium.find_element_by_name('login').click()
        self.select_element_by_name_wait(selenium, 5, 'loginOut')
        self.assertEquals('Welcome', selenium.title)
        self.selenium2 = webdriver.Firefox()
        selenium2 = self.selenium2
        selenium2.implicitly_wait(10)
        selenium2.get(f'{self.live_server_url}/')
        username = selenium2.find_element_by_name('username')
        username.send_keys('usuario')
        password = selenium2.find_element_by_name('password')
        password.send_keys('usuario')
        selenium2.find_element_by_name('login').click()
        time.sleep(2)
        self.assertEquals('Esperando autorizacion', selenium2.title)
        self.select_element_by_class_name(selenium, 10, 'btn-success').click()
        self.select_element_by_name_wait(selenium2, 10, 'loginOut')
        self.assertEquals('Welcome', selenium2.title)
        time.sleep(2)

        self.user = User.objects.create_user(
            username='usuario_New',
            password='usuario'
        )
        self.user.is_active = True
        self.user.save()
        self.selenium3 = webdriver.Firefox()
        selenium3 = self.selenium3
        selenium3.implicitly_wait(10)
        selenium3.get(f'{self.live_server_url}/')
        username = selenium3.find_element_by_name('username')
        username.send_keys('usuario_New')
        password = selenium3.find_element_by_name('password')
        password.send_keys('usuario')
        selenium3.find_element_by_name('login').click()
        self.select_element_by_name_wait(selenium3, 5, 'loginOut')
        self.assertEquals('Welcome', selenium.title)
        self.selenium4 = webdriver.Firefox()
        selenium4 = self.selenium4
        selenium4.implicitly_wait(10)
        selenium4.get(f'{self.live_server_url}/')
        username = selenium4.find_element_by_name('username')
        username.send_keys('usuario_New')
        password = selenium4.find_element_by_name('password')
        password.send_keys('usuario')
        selenium4.find_element_by_name('login').click()
        time.sleep(2)
        self.assertEquals('Esperando autorizacion', selenium4.title)
        self.select_element_by_class_name(selenium3, 10, 'btn-success').click()
        self.select_element_by_name_wait(selenium4, 10, 'loginOut')
        self.assertEquals('Welcome', selenium2.title)
        time.sleep(2)
        self.selenium3.quit()
        self.selenium4.quit()

    def login_with_two_successful_session_and_two_of_two_rejected_different_user(self):
        self.user = User.objects.create_user(
            username='usuario',
            password='usuario'
        )
        self.user.is_active = True
        self.user.save()
        self.selenium = webdriver.Firefox()
        selenium = self.selenium
        selenium.implicitly_wait(10)
        selenium.get(f'{self.live_server_url}/')
        username = selenium.find_element_by_name('username')
        username.send_keys('usuario')
        password = selenium.find_element_by_name('password')
        password.send_keys('usuario')
        selenium.find_element_by_name('login').click()
        self.select_element_by_name_wait(selenium, 5, 'loginOut')
        self.assertEquals('Welcome', selenium.title)
        self.selenium2 = webdriver.Firefox()
        selenium2 = self.selenium2
        selenium2.implicitly_wait(10)
        selenium2.get(f'{self.live_server_url}/')
        username = selenium2.find_element_by_name('username')
        username.send_keys('usuario')
        password = selenium2.find_element_by_name('password')
        password.send_keys('usuario')
        selenium2.find_element_by_name('login').click()
        time.sleep(2)
        self.assertEquals('Esperando autorizacion', selenium2.title)
        self.select_element_by_class_name(selenium, 10, 'btn-danger').click()
        time.sleep(2)
        self.assertEquals('Sin permisos', selenium2.title)
        time.sleep(2)

        self.user = User.objects.create_user(
            username='usuario_New',
            password='usuario'
        )
        self.user.is_active = True
        self.user.save()
        self.selenium3 = webdriver.Firefox()
        selenium3 = self.selenium3
        selenium3.implicitly_wait(10)
        selenium3.get(f'{self.live_server_url}/')
        username = selenium3.find_element_by_name('username')
        username.send_keys('usuario_New')
        password = selenium3.find_element_by_name('password')
        password.send_keys('usuario')
        selenium3.find_element_by_name('login').click()
        self.select_element_by_name_wait(selenium3, 5, 'loginOut')
        self.assertEquals('Welcome', selenium.title)
        self.selenium4 = webdriver.Firefox()
        selenium4 = self.selenium4
        selenium4.implicitly_wait(10)
        selenium4.get(f'{self.live_server_url}/')
        username = selenium4.find_element_by_name('username')
        username.send_keys('usuario_New')
        password = selenium4.find_element_by_name('password')
        password.send_keys('usuario')
        selenium4.find_element_by_name('login').click()
        time.sleep(2)
        self.assertEquals('Esperando autorizacion', selenium4.title)
        self.select_element_by_class_name(selenium3, 10, 'btn-danger').click()
        time.sleep(2)
        self.assertEquals('Sin permisos', selenium2.title)
        time.sleep(2)
        self.selenium3.quit()
        self.selenium4.quit()
