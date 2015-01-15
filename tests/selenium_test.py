"""Front-end tests"""
import unittest

from browserid.pages.sign_in import SignIn

from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base = 'http://localhost:8888'


def click_next(self):
    """Clicks the 'next' button."""

    if self.selenium.find_element(*self._desktop_next_locator).is_displayed():
        self.selenium.find_element(*self._desktop_next_locator).click()
    else:
        self.selenium.find_element(*self._mobile_next_locator).click()

        WebDriverWait(self.selenium, self.timeout).until(
            lambda s: not s.find_element(
                *self._checking_email_provider_loading_locator).is_displayed())


class DriverTestBase(unittest.TestCase):
    def setUp(self):
        self.drv = webdriver.Firefox()

    def tearDown(self):
        self.drv.quit()


class AuthTest(DriverTestBase):
    def testLoginAndLogout(self):
        self.drv.get(base + '/')

        self.assertIn('Welcome to <em>Dokomo</em>', self.drv.page_source)

        self.drv.find_element_by_id('login').click()
        persona = SignIn(self.drv, 60)
        persona.email = 'test@mockmyid.com'
        click_next(persona)
        self.drv.switch_to.window(self.drv.window_handles[0])

        self.assertTrue(self.drv.find_element_by_id('logout').is_displayed())
        self.assertIn('Welcome: test@mockmyid.com', self.drv.page_source)

        self.drv.find_element_by_id('logout').click()
        load2 = EC.presence_of_element_located((By.ID, 'login'))
        WebDriverWait(self.drv, 2).until(load2)

        self.assertIn('Welcome to <em>Dokomo</em>', self.drv.page_source)


if __name__ == '__main__':
    unittest.main()
