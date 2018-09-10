# python manage.py test mascotas
from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import time


class AccountTestCase(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_register(self):
        timeout = 2
        selenium = self.selenium

        # Opening the link we want to test
        selenium.get(f'{self.live_server_url}/user/register/')
        # find the form element
        first_name = selenium.find_element_by_name('first_name')
        last_name = selenium.find_element_by_name('last_name')
        username = selenium.find_element_by_name('username')
        email = selenium.find_element_by_name('email')
        password1 = selenium.find_element_by_name('password1')
        password2 = selenium.find_element_by_name('password2')
        submit = selenium.find_element_by_name('regirter')
        # Fill the form with data
        username.send_keys('camila')
        first_name.send_keys('Yusuf')
        last_name.send_keys('Unary')
        email.send_keys('yusufqrii@gmail.com')
        password1.send_keys('qwertyuiop')
        password2.send_keys('qwertyuiop')

        # submitting the form
        submit.send_keys(Keys.RETURN)
        time.sleep(3)
        self.assertEquals("Login", selenium.title)
        # check the returned result
        #assert 'Check your email' in selenium.page_source
