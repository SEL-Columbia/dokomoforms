"""Front-end tests"""
import base64
from distutils.version import StrictVersion
import functools
from http.client import HTTPConnection
import json
import os
import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import dokomoforms.api.survey as survey_api
from dokomoforms import db
from dokomoforms.db.auth_user import auth_user_table
from dokomoforms.db.submission import submission_table
from dokomoforms.db.survey import survey_table
from dokomoforms.settings import SAUCE_USERNAME, SAUCE_ACCESS_KEY, \
    DEFAULT_BROWSER, SAUCE_CONNECT


base = 'http://localhost:8888'

connection = db.engine.connect()


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

        if not SAUCE_CONNECT:
            self.drv = webdriver.Firefox()
            self.browser_name = 'Firefox'
            self.platform = 'Linux'
            return

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
            caps['name'] = ' -- '.join([
                os.environ['TRAVIS_BUILD_NUMBER'],
                self.browser_config,
                self.__class__.__name__])
        else:
            caps['name'] = ' -- '.join([
                'Manual run',
                self.browser_config,
                self.__class__.__name__])

        hub_url = '{}:{}@localhost:4445'.format(self.username, self.access_key)
        cmd_executor = 'http://{}/wd/hub'.format(hub_url)
        self.drv = webdriver.Remote(desired_capabilities=caps,
                                    command_executor=cmd_executor)
        self.drv.implicitly_wait(10)
        self.version = StrictVersion(self.version)

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
        connection.execute(submission_table.delete())
        connection.execute(auth_user_table.delete().where(
            auth_user_table.c.email == 'test@mockmyid.com'))
        self.drv.quit()

        if SAUCE_CONNECT:
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
    def testSubmitSuccessfully(self):  # flake8: noqa
        # Log in
        self.drv.get(base + '/debug/login/test_email')
        self.drv.get(base + '/')

        # Click on the survey
        WebDriverWait(self.drv, 5).until(EC.presence_of_element_located(
            (By.CLASS_NAME,
             'btn-manage'))
        )
        self.drv.find_element_by_class_name(
            'btn-manage'
        ).click()

        # Click on the shareable link
        # WebDriverWait(self.drv, 4).until(EC.presence_of_element_located(
        # (By.XPATH, '/html/body/div[3]/div/a')))
        # self.drv.find_element_by_xpath('/html/body/div[3]/div/a').click()

        # Look into where the link is later...
        survey_id = self.drv.current_url.split('/')[-1]
        self.drv.get(base + '/survey/' + survey_id)

        # Fill out the survey
        self.drv.find_element_by_class_name('start_btn').click()
        WebDriverWait(self.drv, 4).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[3]/div[2]/input')))
        next_class = 'page_nav__next'
        next_button = lambda: self.drv.find_element_by_class_name(next_class)
        in_xpath = '/html/body/div[3]/div[2]/'

        self.drv.find_elements_by_tag_name('input')[0].send_keys('1')
        if self.browser_name == 'safari':
            self.drv.execute_script("$('input').first().change()")
        next_button().click()
        if self.browser_name == 'android':
            self.drv.find_element_by_tag_name('select').click()
            self.drv.switch_to.window('NATIVE_APP')
            self.drv.find_elements_by_tag_name('TextView')[-2].click()
            self.drv.switch_to.window('WEBVIEW_0')
        else:
            self.drv.find_elements_by_tag_name('option')[1].click()
        next_button().click()
        self.drv.find_element_by_tag_name('input').send_keys('3.3')
        if self.browser_name == 'safari':
            self.drv.execute_script("$('input').change()")
        next_button().click()
        if self.browser_name == 'android':
            self.drv.find_element_by_tag_name('input').click()
            self.drv.switch_to.window('NATIVE_APP')
            self.drv.find_element_by_id('button1').click()
            self.drv.switch_to.window('WEBVIEW_0')
        else:
            self.drv.find_element_by_xpath(in_xpath + 'input').send_keys(
                '4/4/44')
            if self.browser_name == 'safari':
                self.drv.execute_script("$('input')[0].value = '4/4/44'")
                self.drv.execute_script("$('input').change()")
        next_button().click()
        if self.browser_name == 'android':
            self.drv.find_element_by_tag_name('input').click()
            self.drv.switch_to.window('NATIVE_APP')
            self.drv.find_element_by_id('button1').click()
            self.drv.switch_to.window('WEBVIEW_0')
        else:
            self.drv.find_element_by_xpath(in_xpath + 'input').send_keys(
                '5:55PM')
            if self.browser_name == 'safari':
                self.drv.execute_script("$('input')[0].value = '5:55PM'")
                self.drv.execute_script("$('input').change()")
        next_button().click()
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
        self.drv.find_element_by_class_name('question__find__btn').click()
        next_button().click()
        self.drv.find_element_by_xpath(in_xpath + 'input').send_keys('text 7')
        if self.browser_name == 'safari':
            self.drv.execute_script("$('input').change()")
        next_button().click()
        if self.browser_name == 'android':
            self.drv.find_element_by_tag_name('select').click()
            self.drv.switch_to.window('NATIVE_APP')
            self.drv.find_elements_by_tag_name('TextView')[-1].click()
            self.drv.switch_to.window('WEBVIEW_0')
        else:
            self.drv.find_elements_by_tag_name('option')[-1].click()
        self.drv.find_element_by_xpath(
            '/html/body/div[3]/input').send_keys('other 8')
        if self.browser_name == 'safari':
            self.drv.execute_script("$('input').change()")
        next_button().click()
        next_button().click()  # note question
        
        WebDriverWait(self.drv, 3).until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'question__radio__span__btn')))
        self.drv.find_element_by_class_name('facility__btn').click()
        self.drv.find_element_by_class_name(
            'facility_name_input').send_keys('new_test_facility')
        if self.browser_name == 'android':
            self.drv.find_element_by_tag_name('select').click()
            self.drv.switch_to.window('NATIVE_APP')
            self.drv.find_elements_by_tag_name('TextView')[-4].click()
            self.drv.switch_to.window('WEBVIEW_0')
        else:
            self.drv.find_elements_by_tag_name('option')[1].click()
        next_button().click()

        self.drv.find_elements_by_tag_name('input')[0].send_keys(
            'super cool ghost submitter')
        self.drv.find_element_by_class_name('submit_btn').click()
        self.drv.find_element_by_class_name('sync_btn').click()

        # Check the submissions
        self.drv.get(base + '/view/'+survey_id)
        WebDriverWait(self.drv, 5).until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'btn-view-submission')
        ))
        submission_link = self.drv.find_element_by_class_name(
            'btn-view-submission')
        self.drv.execute_script(
            'window.scrollTo(0, {});'.format(submission_link.location['y']))
        submission_link.click()

        # Check the submission
        self.assertIn('Submission Detail', self.drv.page_source)
        self.assertIn('1. choice 1', self.drv.page_source)
        self.assertIn('3.3', self.drv.page_source)
        self.assertIn('4. date question',
                      self.drv.page_source)
        self.assertIn('5. time question',
                      self.drv.page_source)
        self.assertIn('[-70, 40]', self.drv.page_source)
        self.assertIn('text 7', self.drv.page_source)
        self.assertIn('other 8', self.drv.page_source)
        self.assertIn('10. facility question',
                      self.drv.page_source)


class TypeTest(DriverTest):

    def tearDown(self):
        super().tearDown()
        connection.execute(survey_table.delete().where(
            survey_table.c.survey_title.like('test_question_type_%')))

    def _create_survey(self, type_constraint_name,
                       allow_multiple=False,
                       choices=None):
        tcn = type_constraint_name
        survey_json = {'email': 'test_email',
                       'survey_title': 'test_question_type_' + tcn,
                       'survey_metadata': {},
                       'questions': [{'question_title': tcn,
                                      'type_constraint_name': tcn,
                                      'allow_multiple': allow_multiple,
                                      'question_to_sequence_number': -1,
                                      'logic': {
                                          'required': False,
                                          'allow_other': False,
                                          'allow_dont_know': False
                                      },
                                      'hint': None,
                                      'choices': choices,
                                      'branches': None}]}

        survey = survey_api.create(connection, survey_json)['result']
        survey_id = survey['survey_id']
        question_id = survey['questions'][0]['question_id']
        return survey_id, question_id


class IntegerTest(TypeTest):

    @report_success_status
    def testDetailDisplay(self):
        # Create the survey
        survey_id, question_id = self._create_survey('integer')

        # Get the survey
        self.drv.get(base + '/survey/' + survey_id)

        # Fill it out
        self.drv.find_element_by_class_name('start_btn').click()
        self.drv.find_element_by_tag_name('input').send_keys('2')
        if self.browser_name == 'safari':
            self.drv.execute_script("$('input').change()")
        self.drv.find_element_by_class_name('page_nav__next').click()
        self.drv.find_element_by_class_name('submit_btn').click()
        self.drv.find_element_by_class_name('sync_btn').click()

        # Log in
        self.drv.get(base + '/debug/login/test_email')

        # Go to the survey data page
        self.drv.get(base + '/view/data/' + survey_id)

        # Test it
        self.drv.find_element_by_css_selector('.question-type-integer').click()
        stats = self.drv.find_element_by_css_selector(
            '.question-type-integer + .question-stats')
        self.assertTrue(stats.is_displayed())

        # WebDriverWait(self.drv, 5).until(
        #     EC.presence_of_element_located((By.ID, 'bar_graph')))
        # bar_graph = self.drv.find_element_by_id('bar_graph')
        # self.assertTrue(bar_graph.is_displayed())


class DecimalTest(TypeTest):

    @report_success_status
    def testDetailDisplay(self):
        # Create the survey
        survey_id, question_id = self._create_survey('decimal')

        # Get the survey
        self.drv.get(base + '/survey/' + survey_id)

        # Fill it out
        self.drv.find_element_by_class_name('start_btn').click()
        self.drv.find_element_by_tag_name('input').send_keys('3.5')
        if self.browser_name == 'safari':
            self.drv.execute_script("$('input').change()")
        self.drv.find_element_by_class_name('page_nav__next').click()
        self.drv.find_element_by_class_name('submit_btn').click()
        self.drv.find_element_by_class_name('sync_btn').click()

        # Log in
        self.drv.get(base + '/debug/login/test_email')

        # Get the visualization page
        self.drv.get(base + '/visualize/' + question_id)

        # Test it
        line_graph = self.drv.find_element_by_id('line_graph')
        self.assertTrue(line_graph.is_displayed())

        WebDriverWait(self.drv, 5).until(
            EC.presence_of_element_located((By.ID, 'bar_graph')))
        bar_graph = self.drv.find_element_by_id('bar_graph')
        self.assertTrue(bar_graph.is_displayed())


class TextTest(TypeTest):

    @report_success_status
    def testDetailDisplay(self):
        # Create the survey
        survey_id, question_id = self._create_survey('text')

        # Get the survey
        self.drv.get(base + '/survey/' + survey_id)

        # Fill it out
        self.drv.find_element_by_class_name('start_btn').click()
        self.drv.find_element_by_tag_name('input').send_keys('some text')
        if self.browser_name == 'safari':
            self.drv.execute_script("$('input').change()")
        self.drv.find_element_by_class_name('page_nav__next').click()
        self.drv.find_element_by_class_name('submit_btn').click()
        self.drv.find_element_by_class_name('sync_btn').click()

        # Log in
        self.drv.get(base + '/debug/login/test_email')

        # Get the visualization page
        self.drv.get(base + '/visualize/' + question_id)

        # Test it
        self.assertRaises(NoSuchElementException, self.drv.find_element_by_id,
                          'line_graph')

        WebDriverWait(self.drv, 5).until(
            EC.presence_of_element_located((By.ID, 'bar_graph')))
        bar_graph = self.drv.find_element_by_id('bar_graph')
        self.assertTrue(bar_graph.is_displayed())


class DateTest(TypeTest):

    @report_success_status
    def testDetailDisplay(self):
        # Create the survey
        survey_id, question_id = self._create_survey('date')

        # Get the survey
        self.drv.get(base + '/survey/' + survey_id)

        # Fill it out
        self.drv.find_element_by_class_name('start_btn').click()
        if self.browser_name == 'android':
            self.drv.find_element_by_tag_name('input').click()
            self.drv.switch_to.window('NATIVE_APP')
            self.drv.find_element_by_id('button1').click()
            self.drv.switch_to.window('WEBVIEW_0')
        else:
            is_safari = self.browser_name == 'safari'
            self.drv.find_element_by_tag_name('input').send_keys('4/4/44')
            if is_safari:
                self.drv.execute_script("$('input')[0].value = '4/4/44'")
                self.drv.execute_script("$('input').change()")
        self.drv.find_element_by_class_name('page_nav__next').click()
        self.drv.find_element_by_class_name('submit_btn').click()
        self.drv.find_element_by_class_name('sync_btn').click()

        # Log in
        self.drv.get(base + '/debug/login/test_email')

        # Get the visualization page
        self.drv.get(base + '/visualize/' + question_id)

        # Test it
        self.assertRaises(NoSuchElementException, self.drv.find_element_by_id,
                          'line_graph')

        WebDriverWait(self.drv, 5).until(
            EC.presence_of_element_located((By.ID, 'bar_graph')))
        bar_graph = self.drv.find_element_by_id('bar_graph')
        self.assertTrue(bar_graph.is_displayed())


class TimeTest(TypeTest):

    @report_success_status
    def testDetailDisplay(self):
        # Create the survey
        survey_id, question_id = self._create_survey('time')

        # Get the survey
        self.drv.get(base + '/survey/' + survey_id)

        # Fill it out
        self.drv.find_element_by_class_name('start_btn').click()
        if self.browser_name == 'android':
            self.drv.find_element_by_tag_name('input').click()
            self.drv.switch_to.window('NATIVE_APP')
            self.drv.find_element_by_id('button1').click()
            self.drv.switch_to.window('WEBVIEW_0')
        else:
            self.drv.find_element_by_tag_name('input').send_keys('5:55PM')
            if self.browser_name == 'safari':
                self.drv.execute_script("$('input')[0].value = '5:55PM'")
                self.drv.execute_script("$('input').change()")
        self.drv.find_element_by_class_name('page_nav__next').click()
        self.drv.find_element_by_class_name('submit_btn').click()
        self.drv.find_element_by_class_name('sync_btn').click()

        # Log in
        self.drv.get(base + '/debug/login/test_email')

        # Get the visualization page
        self.drv.get(base + '/visualize/' + question_id)

        # Test it
        self.assertRaises(NoSuchElementException,
                          self.drv.find_element_by_id,
                          'line_graph')

        WebDriverWait(self.drv, 5).until(
            EC.presence_of_element_located((By.ID, 'bar_graph')))
        bar_graph = self.drv.find_element_by_id('bar_graph')
        self.assertTrue(bar_graph.is_displayed())


class MultipleChoiceTest(TypeTest):

    @report_success_status
    def testDetailDisplay(self):
        # Create the survey
        survey_id, question_id = self._create_survey('multiple_choice',
                                                     choices=['only choice'])

        # Get the survey
        self.drv.get(base + '/survey/' + survey_id)

        # Fill it out
        self.drv.find_element_by_class_name('start_btn').click()
        self.drv.find_elements_by_tag_name('option')[1].click()
        self.drv.find_element_by_class_name('page_nav__next').click()

        WebDriverWait(self.drv, 5).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'submit_btn')
            )
        )
        self.drv.find_element_by_class_name('submit_btn').click()
        self.drv.find_element_by_class_name('sync_btn').click()

        # Log in
        self.drv.get(base + '/debug/login/test_email')

        # Get the visualization page
        self.drv.get(base + '/visualize/' + question_id)

        # Test it
        self.assertRaises(NoSuchElementException,
                          self.drv.find_element_by_id,
                          'line_graph')

        WebDriverWait(self.drv, 10).until(
            EC.presence_of_element_located((By.ID, 'bar_graph')))
        bar_graph = self.drv.find_element_by_id('bar_graph')
        self.assertTrue(bar_graph.is_displayed())


class MultiSelectTest(TypeTest):

    @report_success_status
    def testDetailDisplay(self):
        # Create the survey
        survey_id, question_id = self._create_survey(
            'multiple_choice',
            allow_multiple=True,
            choices=['choice 1', 'choice 2'])

        # Get the survey
        self.drv.get(base + '/survey/' + survey_id)

        # Fill it out
        self.drv.find_element_by_class_name('start_btn').click()
        if self.browser_name == 'android':
            self.drv.find_element_by_tag_name('select').click()
            self.drv.switch_to.window('NATIVE_APP')
            choices = self.drv.find_elements_by_tag_name('CheckedTextView')
            choices[1].click()
            choices[2].click()
            # Click "OK"
            self.drv.find_elements_by_tag_name('Button')[-1].click()
            self.drv.switch_to.window('WEBVIEW_0')
        elif self.browser_name in {'safari', 'internet explorer'}:
            # The COMMAND key approach fails due to
            # https://code.google.com/p/selenium/issues/detail?id=4136
            # I think...
            self.drv.execute_script('''
               var choices = $('option');
               choices[1].selected = true;
               choices[2].selected = true;
            ''')
            self.drv.execute_script("$('select').change()")
        else:
            is_osx = self.platform.startswith('OS X')
            ctrl_key = Keys.COMMAND if is_osx else Keys.CONTROL
            choices = self.drv.find_elements_by_tag_name('option')
            ActionChains(
                self.drv
            ).key_down(
                ctrl_key
            ).click(
                choices[1]
            ).click(
                choices[2]
            ).key_up(
                ctrl_key
            ).perform()
        self.drv.find_element_by_class_name('page_nav__next').click()

        WebDriverWait(self.drv, 5).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'submit_btn')
            )
        )
        self.drv.find_element_by_class_name('submit_btn').click()
        self.drv.find_element_by_class_name('sync_btn').click()

        # Log in
        self.drv.get(base + '/debug/login/test_email')

        # Get the submission page
        self.drv.get(base + '/view/' + survey_id)
        WebDriverWait(self.drv, 5).until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'btn-view-submission')
        ))
        submission_link = self.drv.find_element_by_class_name(
            'btn-view-submission')
        self.drv.execute_script(
            'window.scrollTo(0, {});'.format(submission_link.location['y']))
        submission_link.click()

        # Test it
        self.assertEqual(
            len(self.drv.find_elements_by_xpath(
                '/html/body/div[3]/div/div[2]/div/ul/li'
            )),
            2
        )

        # Get the visualization page
        self.drv.get(base + '/visualize/' + question_id)

        # Test it
        self.assertRaises(NoSuchElementException,
                          self.drv.find_element_by_id,
                          'line_graph')

        WebDriverWait(self.drv, 5).until(
            EC.presence_of_element_located((By.ID, 'bar_graph')))
        bar_graph = self.drv.find_element_by_id('bar_graph')
        self.assertTrue(bar_graph.is_displayed())


class LocationTest(TypeTest):

    @report_success_status
    def testDetailDisplay(self):
        # Create the survey
        survey_id, question_id = self._create_survey('location')

        # Get the survey
        self.drv.get(base + '/survey/' + survey_id)

        # Fill it out
        self.drv.find_element_by_class_name('start_btn').click()
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
        self.drv.find_element_by_class_name('question__find__btn').click()
        self.drv.find_element_by_class_name('page_nav__next').click()
        self.drv.find_element_by_class_name('submit_btn').click()
        self.drv.find_element_by_class_name('sync_btn').click()

        # Log in
        self.drv.get(base + '/debug/login/test_email')

        # Get the visualization page
        self.drv.get(base + '/visualize/' + question_id)

        # Test it
        self.assertRaises(NoSuchElementException,
                          self.drv.find_element_by_id,
                          'line_graph')

        WebDriverWait(self.drv, 10).until(
            EC.presence_of_element_located((By.ID, 'bar_graph')))
        bar_graph = self.drv.find_element_by_id('bar_graph')
        self.assertTrue(bar_graph.is_displayed())

        # TODO: The map doesn't show up anymore... but it looks like @jmwohl
        # hasn't included the submission map in the admin interface yet.
        # vis_map = self.drv.find_element_by_id('vis_map')
        # self.assertTrue(vis_map.is_displayed())


if __name__ == '__main__':
    unittest.main()

