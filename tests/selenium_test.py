"""Front-end tests"""
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tornado.web
import tornado.ioloop
from tornado.testing import AsyncHTTPTestCase

from webapp import pages, config

base = 'http://localhost:8888'


def go_to_new_window(driver: WebDriver):
    """
    I think this is how you switch windows...?

    :param driver: the Selenium WebDriver
    """
    for handle in driver.window_handles:
        driver.switch_to.window(handle)


class DriverTest(AsyncHTTPTestCase):
    def setUp(self):
        super(DriverTest, self).setUp()
        self.drv = webdriver.Firefox()
        self.get_app()

    def tearDown(self):
        super(DriverTest, self).tearDown()
        self.drv.quit()

    def get_app(self):
        self.app = tornado.web.Application(pages, **config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()


class AuthTest(DriverTest):
    def testLoginAndLogout(self):
        self.drv.get(base + '/')

        self.assertIn('Welcome to <em>Dokomo</em>', self.drv.page_source)

        self.drv.find_element_by_xpath('//*[@id="login"]').click()
        go_to_new_window(self.drv)
        eml = self.drv.find_element_by_xpath('//*[@id="authentication_email"]')
        eml.send_keys('test@mockmyid.com', Keys.RETURN)
        self.drv.switch_to.window(self.drv.window_handles[0])
        load = EC.presence_of_element_located((By.CLASS_NAME, 'center-create'))
        WebDriverWait(self.drv, 10).until(load)

        self.assertIn('Welcome: test@mockmyid.com', self.drv.page_source)

        self.drv.find_element_by_id('logout').click()
        load2 = EC.presence_of_element_located((By.ID, 'login'))
        WebDriverWait(self.drv, 2).until(load2)

        self.assertIn('Welcome to <em>Dokomo</em>', self.drv.page_source)


if __name__ == '__main__':
    unittest.main()
