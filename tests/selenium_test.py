"""Front-end tests"""
import base64
import functools
from http.client import HTTPConnection
import json
import os
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from db.auth_user import auth_user_table
from db.submission import submission_table
from settings import SAUCE_USERNAME, SAUCE_ACCESS_KEY, DEFAULT_BROWSER


base = 'http://localhost:8888'


def go_to_new_window(driver: WebDriver):
    """
    I think this is how you switch windows...?

    :param driver: the Selenium WebDriver
    """
    for handle in driver.window_handles:
        driver.switch_to.window(handle)


def report_success_status(method):
    @functools.wraps(method)
    def set_passed(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self.passed = True
        return result

    return set_passed


class DriverTest(unittest.TestCase):
    def setUp(self):
        self.passed = False

        self.username = os.environ.get('SAUCE_USERNAME', SAUCE_USERNAME)
        self.access_key = os.environ.get('SAUCE_ACCESS_KEY', SAUCE_ACCESS_KEY)
        self.browser_config = os.environ.get('BROWSER', DEFAULT_BROWSER)
        bconf = self.browser_config.split(':')
        self.browser_name, self.version, self.platform, *other = bconf
        caps = {'browserName': self.browser_name,
                'platform': self.platform}
        if self.browser_name in {'android', 'iPhone'}:
            caps['deviceName'] = other[0]
            caps['device-orientation'] = 'portrait'
        if self.version:
            caps['version'] = self.version
        if 'TRAVIS_JOB_NUMBER' in os.environ:
            caps['tunnel-identifier'] = os.environ['TRAVIS_JOB_NUMBER']
            caps['build'] = os.environ['TRAVIS_BUILD_NUMBER']
            caps['tags'] = [os.environ['TRAVIS_PYTHON_VERSION'], 'CI']
            caps['name'] = ' -- '.join([os.environ['TRAVIS_BUILD_NUMBER'],
                                        self.browser_config])
        else:
            caps['name'] = 'Manual run -- ' + self.browser_config
        hub_url = '{}:{}@localhost:4445'.format(self.username, self.access_key)
        cmd_executor = 'http://{}/wd/hub'.format(hub_url)
        self.drv = webdriver.Remote(desired_capabilities=caps,
                                    command_executor=cmd_executor)
        self.drv.implicitly_wait(10)

    def _set_sauce_status(self):
        credential_s = ':'.join([self.username, self.access_key])
        credential_b = credential_s.encode('utf-8')
        auth = base64.encodebytes(credential_b)[:-1]
        body = json.dumps({'passed': self.passed})
        connection = HTTPConnection('saucelabs.com')
        path = '/rest/v1/{}/jobs/{}'.format(self.username, self.drv.session_id)
        headers = {'Authorization': 'Basic ' + auth.decode('utf-8')}
        connection.request('PUT', path, body, headers=headers)

    def tearDown(self):
        submission_table.delete().execute()
        auth_user_table.delete().where(
            auth_user_table.c.email == 'test@mockmyid.com').execute()
        self.drv.quit()

        self._set_sauce_status()


# This test doesn't play nice with Sauce Labs, and I'm confident that
# Persona works anyway...

# class AuthTest(DriverTest):
# def testLoginAndLogout(self):
# self.drv.get(base + '/')
#
# self.assertIn('Welcome to <em>Dokomo</em>', self.drv.page_source)
#
# self.drv.find_element_by_xpath('//*[@id="login"]').click()
# go_to_new_window(self.drv)
# eml = self.drv.find_element_by_xpath('//*[
# @id="authentication_email"]')
# eml.send_keys('test@mockmyid.com', Keys.RETURN)
# self.drv.switch_to.window(self.drv.window_handles[0])
# load = EC.presence_of_element_located((By.ID, 'logout'))
# WebDriverWait(self.drv, 10).until(load)
#
# self.assertIn('Welcome: test@mockmyid.com', self.drv.page_source)
#
# self.drv.find_element_by_id('logout').click()
# load2 = EC.presence_of_element_located((By.ID, 'login'))
# WebDriverWait(self.drv, 2).until(load2)
#
# self.assertIn('Welcome to <em>Dokomo</em>', self.drv.page_source)


class SubmissionTest(DriverTest):
    @report_success_status
    def testSubmitSuccessfully(self):
        # Log in
        self.drv.get(base + '/debug/login/test_email')
        self.drv.get(base + '/')

        # Click on the survey
        self.drv.find_element_by_xpath('/html/body/div[3]/div/ul/li/a').click()

        # Click on the shareable link
        WebDriverWait(self.drv, 2).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[2]/div/a')))
        self.drv.find_element_by_xpath(
            '/html/body/div[2]/div/a').click()

        # Fill out the survey
        WebDriverWait(self.drv, 2).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[3]/input')))
        next_button = self.drv.find_element_by_class_name('page_nav__next')
        in_xpath = '/html/body/div[3]/'

        self.drv.find_element_by_xpath(in_xpath + 'input').send_keys('1')
        next_button.click()
        self.drv.find_element_by_xpath(in_xpath + 'select/option[2]').click()
        next_button.click()
        self.drv.find_element_by_xpath(in_xpath + 'input').send_keys('3.3')
        next_button.click()
        if self.browser_name == 'android':
            self.drv.find_element_by_xpath(in_xpath + 'input').click()
            self.drv.switch_to.window('NATIVE_APP')
            self.drv.find_element_by_id('button1').click()
            self.drv.switch_to.window('WEBVIEW_0')
            next_button = self.drv.find_element_by_class_name('page_nav__next')
        else:
            self.drv.find_element_by_xpath(in_xpath + 'input').send_keys(
                '4/4/44')
        next_button.click()
        if self.browser_name == 'android':
            self.drv.find_element_by_xpath(in_xpath + 'input').click()
            self.drv.switch_to.window('NATIVE_APP')
            self.drv.find_element_by_id('button1').click()
            self.drv.switch_to.window('WEBVIEW_0')
            next_button = self.drv.find_element_by_class_name('page_nav__next')
        else:
            self.drv.find_element_by_xpath(in_xpath + 'input').send_keys(
                '5:55')
        next_button.click()
        # browser geolocation is complicated in selenium...
        self.drv.execute_script(
            '''
            window.navigator.geolocation.getCurrentPosition =
              function (success) {
                var position = {"coords": {"latitude":  "40",
                                           "longitude": "-70"}
                               };
                success(position);
              }
            '''
        )
        self.drv.find_element_by_class_name('question__btn').click()
        next_button.click()
        self.drv.find_element_by_xpath(in_xpath + 'input').send_keys('text 7')
        next_button.click()
        self.drv.find_element_by_id('with_other').click()
        self.drv.find_element_by_xpath(in_xpath + 'input').send_keys('other 8')
        next_button.click()
        next_button.click()  # note question
        WebDriverWait(self.drv, 3).until(EC.presence_of_element_located(
            (By.XPATH, in_xpath + 'div[3]/input')))
        self.drv.find_element_by_xpath(in_xpath + 'div[3]/input').send_keys(
            'new_test_facility')
        self.drv.find_element_by_xpath(in_xpath + 'div[4]/span[2]').click()
        next_button.click()

        self.drv.find_element_by_xpath(in_xpath + 'div[2]/input').send_keys(
            'super cool ghost submitter')
        self.drv.find_element_by_class_name('question__btn').click()

        WebDriverWait(self.drv, 3).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[3]/input')))

        # Check the submissions
        self.drv.get(base + '/')
        WebDriverWait(self.drv, 3).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[3]/div/ul/li/a')))
        self.drv.find_element_by_xpath(
            '/html/body/div[3]/div/ul/li/a').click()
        submission_link = self.drv.find_element_by_xpath(
            '/html/body/div[2]/div/ul[2]/li/a')
        self.drv.execute_script(
            'window.scrollTo(0, {});'.format(submission_link.location['y']))
        submission_link.click()
        # Check the submission
        WebDriverWait(self.drv, 3).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[2]/div/ul/li')))
        self.assertIn('Answer: 1', self.drv.page_source)
        self.assertIn('Choice: 1. choice 1', self.drv.page_source)
        self.assertIn('Answer: 3.3', self.drv.page_source)
        self.assertIn('<strong>4. date question</strong><br',
                      self.drv.page_source)
        self.assertIn('<strong>5. time question</strong><br',
                      self.drv.page_source)
        self.assertIn('Answer: [-70, 40]', self.drv.page_source)
        self.assertIn('Answer: [-70, 40]', self.drv.page_source)
        self.assertIn('Answer: other 8', self.drv.page_source)
        self.assertIn('<strong>10. facility question</strong><br',
                      self.drv.page_source)


if __name__ == '__main__':
    unittest.main()

