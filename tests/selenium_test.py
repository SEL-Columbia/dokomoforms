"""Front-end tests"""
import unittest

from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base = 'http://localhost:8888'


def go_to_new_window(driver: WebDriver):
    """
    I think this is how you switch windows...?

    :param driver: the Selenium WebDriver
    """
    for handle in driver.window_handles:
        driver.switch_to.window(handle)


class DriverTest(unittest.TestCase):
    def setUp(self):
        self.drv = webdriver.Firefox()

    def tearDown(self):
        self.drv.quit()


class AuthTest(DriverTest):
    def testLoginAndLogout(self):
        self.drv.get(base + '/')

        self.assertIn('Welcome to <em>Dokomo</em>', self.drv.page_source)

        self.drv.find_element_by_xpath('//*[@id="login"]').click()
        go_to_new_window(self.drv)
        eml = self.drv.find_element_by_xpath('//*[@id="authentication_email"]')
        eml.send_keys('test@mockmyid.com', Keys.RETURN)
        self.drv.switch_to.window(self.drv.window_handles[0])
        load = EC.presence_of_element_located((By.ID, 'logout'))
        WebDriverWait(self.drv, 30).until(load)

        self.assertIn('Welcome: test@mockmyid.com', self.drv.page_source)

        self.drv.find_element_by_id('logout').click()
        load2 = EC.presence_of_element_located((By.ID, 'login'))
        WebDriverWait(self.drv, 2).until(load2)

        self.assertIn('Welcome to <em>Dokomo</em>', self.drv.page_source)


if __name__ == '__main__':
    unittest.main()
