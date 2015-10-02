"""Front end tests."""
import base64
import datetime
from decimal import Decimal
from distutils.version import StrictVersion
import functools
import json
from http.client import HTTPConnection
import os
import re
import signal
import sys
import time
import unittest
from urllib.request import urlopen
import urllib.error

from bs4 import BeautifulSoup

import dateutil.parser

from passlib.hash import bcrypt_sha256

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import tests.python.util
from tests.python.util import setUpModule, tearDownModule
util = (setUpModule, tearDownModule)

import config
SAUCE_CONNECT = getattr(config, 'SAUCE_CONNECT', False)
if not SAUCE_CONNECT:
    SAUCE_CONNECT = os.environ.get('SAUCE_CONNECT', 'f').startswith('t')
SAUCE_USERNAME = getattr(config, 'SAUCE_USERNAME', None)
SAUCE_ACCESS_KEY = getattr(config, 'SAUCE_ACCESS_KEY', None)
DEFAULT_BROWSER = getattr(config, 'DEFAULT_BROWSER', None)

from dokomoforms.models import (
    Survey, Submission, Photo, Administrator, Node, Choice, SubSurvey,
    construct_survey, construct_survey_node, construct_node, construct_bucket
)


base = 'http://localhost:9999'


class SauceTestTooLong(Exception):
    pass


class DriverTakingTooLong(Exception):
    pass


def too_long(exception_class):
    def alarm(signum, frame):
        raise exception_class()
    return alarm


def attempt_a_sauce_test(self, method, *args, **kwargs):
    is_travis = os.environ.get('TRAVIS', 'f').startswith('t')
    if is_travis:
        signal.signal(signal.SIGALRM, too_long(SauceTestTooLong))
        countdown = 360 if self.browser == 'android' else 240
        signal.alarm(countdown)
    try:
        result = method(self, *args, **kwargs)
    finally:
        if is_travis:
            signal.alarm(0)
    self.passed = True
    return result


def report_success_status(method):
    @functools.wraps(method)
    def set_passed(self, *args, **kwargs):
        if not SAUCE_CONNECT:
            return method(self, *args, **kwargs)
        num_attempts = 3
        for attempt in range(num_attempts):
            try:
                return attempt_a_sauce_test(self, method, *args, **kwargs)
            except unittest.SkipTest:
                self.passed = True
                raise
            except (SauceTestTooLong, TimeoutException):
                print(
                    'timeout {} -- {}'.format(attempt, self._testMethodName),
                    file=sys.stderr
                )
                if attempt == num_attempts - 1:
                    raise
                self.drv.quit()
                self.setUp()
    return set_passed


class DriverTest(tests.python.util.DokoExternalDBTest):
    def start_remote_webdriver(self):
        signal.signal(signal.SIGALRM, too_long(DriverTakingTooLong))
        countdown = 120 if self.browser == 'android' else 60
        signal.alarm(countdown)
        try:
            return webdriver.Remote(**self.driver_config)
        finally:
            signal.alarm(0)

    def setUp(self):
        try:
            urlopen(base)
        except urllib.error.URLError:
            self.fail(
                'The webapp is not running on port 9999.\n'
                'You may want to execute ./tests/python/selenium_webapp.py'
                ' &>/dev/null &'
            )
        super().setUp()

        self.passed = False
        self.online = True

        f_profile = webdriver.FirefoxProfile()
        f_profile.set_preference('media.navigator.permission.disabled', True)
        f_profile.update_preferences()

        if not SAUCE_CONNECT:
            self.drv = webdriver.Firefox(firefox_profile=f_profile)
            self.browser = 'firefox'
            self.platform = 'Linux'
            return

        self.username = os.environ.get('SAUCE_USERNAME', SAUCE_USERNAME)
        self.access_key = os.environ.get('SAUCE_ACCESS_KEY', SAUCE_ACCESS_KEY)
        browser_config = os.environ.get('BROWSER', DEFAULT_BROWSER)
        values = (self.username, self.access_key, browser_config)
        if any(v is None for v in values):
            self.fail(
                'You have specified SAUCE_CONNECT=true but you have not'
                ' specified SAUCE_USERNAME, SAUCE_ACCESS_KEY,'
                ' and DEFAULT_BROWSER'
            )
        configs = browser_config.split(':')
        self.browser, self.version, self.platform, *other = configs
        caps = {
            'browserName': self.browser,
            'platform': self.platform,
            'idleTimeout': 1000,  # maximum
        }
        if self.browser in {'android', 'iPhone'}:
            caps['deviceName'] = other[0]
            caps['device-orientation'] = 'portrait'
        if self.version:
            caps['version'] = self.version
        self.version = StrictVersion(self.version)
        if 'TRAVIS_JOB_NUMBER' in os.environ:
            caps['tunnel-identifier'] = os.environ['TRAVIS_JOB_NUMBER']
            caps['build'] = os.environ['TRAVIS_BUILD_NUMBER']
            caps['tags'] = [os.environ['TRAVIS_PYTHON_VERSION'], 'CI']
            caps['name'] = ' -- '.join((
                os.environ['TRAVIS_BUILD_NUMBER'],
                browser_config,
                '{}.{}'.format(self.__class__.__name__, self._testMethodName)
            ))
        else:
            caps['name'] = ' -- '.join((
                'Manual run',
                browser_config,
                '{}.{}'.format(self.__class__.__name__, self._testMethodName)
            ))
        hub_url = '{}:{}@localhost:4445'.format(self.username, self.access_key)
        cmd_executor = 'http://{}/wd/hub'.format(hub_url)
        browser_profile = None
        if self.browser == 'firefox':
            browser_profile = f_profile
        elif self.browser == 'chrome':
            caps['disable-user-media-security'] = True
        self.driver_config = {
            'desired_capabilities': caps,
            'command_executor': cmd_executor,
            'browser_profile': browser_profile,
        }
        num_attempts = 3
        for attempt in range(num_attempts):
            try:
                self.drv = self.start_remote_webdriver()
                break
            except urllib.error.URLError:
                self.fail(
                    'Sauce Connect failure. Did you start Sauce Connect?'
                )
            except DriverTakingTooLong:
                print('webdriver {}'.format(attempt))
                if attempt == num_attempts - 1:
                    raise
        self.drv.implicitly_wait(10)
        if self.platform == 'Windows 8.1':
            time.sleep(10)
        if self.browser != 'android':
            self.drv.set_page_load_timeout(180)
        self.drv.set_script_timeout(180)

    def _set_sauce_status(self):
        credentials = '{}:{}'.format(self.username, self.access_key).encode()
        auth = base64.encodebytes(credentials)[:-1].decode()
        body = json.dumps({'passed': self.passed})
        connection = HTTPConnection('saucelabs.com')
        path = '/rest/v1/{}/jobs/{}'.format(self.username, self.drv.session_id)
        headers = {'Authorization': 'Basic {}'.format(auth)}
        connection.request('PUT', path, body, headers=headers)
        connection.close()

    def tearDown(self):
        super().tearDown()

        try:
            urlopen('http://localhost:9999/debug/toggle_facilities?state=true')
        except urllib.error.URLError:
            pass

        try:
            self.drv.quit()
        except ProcessLookupError:
            pass

        if SAUCE_CONNECT:
            self._set_sauce_status()

    def get(self, path):
        self.drv.get(base + path)

    def switch_window(self, go_back=False):
        window_handles = self.drv.window_handles
        if not go_back:
            window_handles = reversed(window_handles)
        for handle in window_handles:
            self.drv.switch_to.window(handle)
            return

    def wait_for_element(self, identifier, by=By.ID, timeout=5, visible=False):
        visibility = EC.visibility_of_element_located
        presence = EC.presence_of_element_located
        loader = visibility if visible else presence
        load = loader((by, identifier))
        WebDriverWait(self.drv, timeout).until(load)

    def sleep(self, duration=None):
        default_duration = 1.25 if SAUCE_CONNECT else 0.25
        if duration is None:
            duration = default_duration
        time.sleep(max(duration, default_duration))

    def set_geolocation(self, lat=40, lng=-70):
        self.sleep()
        self.drv.execute_script(
            '''
            window.navigator.geolocation.getCurrentPosition =
              function (success) {{
                var position = {{
                  "coords": {{"latitude": {}, "longitude": {}}}
                }};
                success(position);
              }};
            '''.format(lat, lng)
        )
        self.sleep()

    def click(self, element):
        element.click()
        self.sleep()

    def toggle_online(self, browser=True, revisit=True):
        if browser:
            self.online = not self.online
            self.drv.execute_script(
                "navigator.__defineGetter__('onLine', function()"
                " {{return {}}});".format(str(self.online).lower())
            )
        if revisit:
            urlopen('http://localhost:9999/debug/toggle_facilities')
        self.sleep(1)

    @property
    def control_key(self):
        is_osx = self.platform.startswith('OS X')
        return Keys.COMMAND if is_osx else Keys.CONTROL

    def enter_date(self, element, year, month, day):
        if self.browser == 'chrome':
            element.send_keys(month)
            self.sleep()
            element.send_keys(day)
            self.sleep()
            element.send_keys(year)
            self.sleep()
        else:
            element.send_keys('/'.join((year, month, day)))

    def enter_time(self, element, hour, minute, am_pm):
        if self.browser == 'chrome':
            element.send_keys(hour)
            self.sleep()
            element.send_keys(minute)
            self.sleep()
            element.send_keys(am_pm)
            self.sleep()
        else:
            element.send_keys('{}:{} {}'.format(hour, minute, am_pm))

    def enter_timestamp(self, element, year, month, day, hour, minute, am_pm):
        if self.browser == 'chrome':
            raise unittest.SkipTest('Selenium + Chrome + timestamp == 😢')
        self.enter_date(element, year, month, day)
        if self.browser == 'chrome':
            # For some reason this doesn't work...
            element.send_keys(Keys.TAB)
        else:
            element.send_keys(' ')
        self.enter_time(element, hour, minute, am_pm)

    def enter_timestamp_temporary(self, e, y, mo, d, h, mi, am_pm):
        """Use this temporarily until we use moment.js."""
        if self.browser == 'chrome':
            raise unittest.SkipTest('Selenium + Chrome + timestamp == 😢')
        e.send_keys('{}-{}-{}T{}:{}:00Z'.format(
            y, mo, d, h if am_pm.lower().startswith('a') else h + 12, mi
        ))


class TestAuth(DriverTest):
    @report_success_status
    def test_login(self):
        if self.browser == 'android':
            raise unittest.SkipTest("The popup doesn't open in the webview.")
        self.get('/')
        self.wait_for_element('btn-login', By.CLASS_NAME)
        self.click(self.drv.find_elements_by_class_name('btn-login')[-1])
        self.switch_window()
        self.wait_for_element('authentication_email', visible=True)
        (
            self.drv
            .find_element_by_id('authentication_email')
            .send_keys('test@mockmyid.com', Keys.RETURN)
        )
        self.switch_window(go_back=True)
        self.wait_for_element('UserDropdown', timeout=10)
        self.assertIn('Recent Submissions', self.drv.page_source)


class AdminTest(DriverTest):
    def setUp(self):
        super().setUp()
        self.get('/debug/login/test_creator@fixtures.com')


class TestAdminOverview(AdminTest):
    @report_success_status
    def test_account_overview_renders_properly(self):
        self.get('/')
        # Recent submissions table
        self.assertEqual(
            len(self.drv.find_elements_by_class_name('submission-row')),
            5
        )
        # Activity graph
        self.assertIsNotNone(
            self.drv.find_element_by_css_selector('path:nth-child(30)')
        )
        # Surveys table
        rows = self.drv.find_elements_by_css_selector('table#surveys tbody tr')
        self.assertEqual(len(rows), 13)

    @report_success_status
    def test_recent_submissions(self):
        self.get('/')

        self.wait_for_element(
            'tr.submission-row:nth-child(1) > td:nth-child(1)',
            by=By.CSS_SELECTOR
        )
        self.click(self.drv.find_element_by_css_selector(
            'tr.submission-row:nth-child(1) > td:nth-child(1)'
        ))

        self.wait_for_element('stat-label', by=By.CLASS_NAME)

        self.assertGreater(
            len(self.drv.find_elements_by_class_name('stat-label')),
            0
        )

    @report_success_status
    def test_view_data_button(self):
        self.get('/')

        self.wait_for_element(
            'tr.odd:nth-child(1) > td:nth-child(5) > a:nth-child(1)',
            by=By.CSS_SELECTOR
        )
        self.click(self.drv.find_element_by_css_selector(
            'tr.odd:nth-child(1) > td:nth-child(5) > a:nth-child(1)'
        ))

        self.wait_for_element('h3', by=By.TAG_NAME)
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'Survey Data'
        )

    @report_success_status
    def test_manage_survey_button(self):
        self.get('/')

        self.click(self.drv.find_element_by_css_selector(
            'tr.odd:nth-child(1) > td:nth-child(5) > a:nth-child(3)'
        ))

        self.assertEqual(
            self.drv.find_elements_by_tag_name('h4')[0].text,
            'SURVEY INFO'
        )

    @report_success_status
    def test_download_json_button(self):
        self.get('/')

        self.click(self.drv.find_element_by_css_selector(
            'tr.odd:nth-child(1) > td:nth-child(5) > div:nth-child(2) >'
            ' button:nth-child(1)'
        ))
        self.click(self.drv.find_element_by_css_selector(
            '.open > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)'
        ))

        self.switch_window()
        response = BeautifulSoup(self.drv.page_source, 'html.parser')
        json_str = response.find('pre').text
        data = json.loads(json_str)
        self.assertIn('survey_id', data)

    @report_success_status
    def test_download_csv_button(self):
        self.get('/')

        self.click(self.drv.find_element_by_css_selector(
            'tr.odd:nth-child(1) > td:nth-child(5) > div:nth-child(2) >'
            ' button:nth-child(1)'
        ))

        json_button = self.drv.find_element_by_css_selector(
            '.open > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)'
        )
        csv_button = self.drv.find_element_by_css_selector(
            '.open > ul:nth-child(2) > li:nth-child(2) > a:nth-child(1)'
        )
        self.assertEqual(
            json_button.get_attribute('href') + '?format=csv',
            csv_button.get_attribute('href')
        )


class TestAdminSettings(AdminTest):
    def sleep(self, duration=None):
        super().sleep(duration)

        is_travis = os.environ.get('TRAVIS', 'f').startswith('t')
        if is_travis and not SAUCE_CONNECT:
            time.sleep(3)

    @report_success_status
    def test_update_settings(self):
        self.get('/')

        self.wait_for_element('UserDropdown')
        self.click(self.drv.find_element_by_id('UserDropdown'))
        self.sleep()

        nav_list = self.drv.find_elements_by_class_name('nav-settings')
        self.assertEqual(len(nav_list), 1)

        self.sleep()
        self.click(self.drv.find_element_by_class_name('nav-settings'))
        self.wait_for_element('user-name')
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_id('user-name')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('new_user')
            .perform()
        )
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_id('user-email')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('new@email.com')
            .perform()
        )
        save_btn = self.drv.find_element_by_class_name('btn-save-user')
        self.sleep()
        save_btn.click()
        self.sleep()

        self.click(self.drv.find_element_by_id('UserDropdown'))
        self.click(self.drv.find_element_by_class_name('nav-settings'))
        self.wait_for_element('user-name')
        name_val = (
            self.drv
            .find_element_by_id('user-name')
            .get_attribute('value')
        )
        email_val = (
            self.drv
            .find_element_by_id('user-email')
            .get_attribute('value')
        )
        self.assertEqual(name_val, 'new_user')
        self.assertEqual(email_val, 'new@email.com')

        # Check that the values have been updated in the database.
        user = (
            self.session
            .query(Administrator)
            .filter_by(id='b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
            .one()
        )
        self.assertEqual(user.name, 'new_user')
        self.assertEqual(user.emails[0].address, 'new@email.com')

    @report_success_status
    def test_fetch_api_key(self):
        def get_user_token():
            return (
                self.session
                .query(Administrator.token)
                .filter_by(id='b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
                .scalar()
            )
        self.get('/')

        self.wait_for_element('UserDropdown', visible=True)
        self.click(self.drv.find_element_by_id('UserDropdown'))
        self.sleep()

        nav = self.drv.find_elements_by_class_name('nav-settings')
        self.assertEqual(len(nav), 1)

        self.sleep()
        self.click(self.drv.find_element_by_class_name('nav-settings'))
        self.wait_for_element('btn-api-key', by=By.CLASS_NAME)
        self.sleep()
        self.click(self.drv.find_element_by_class_name('btn-api-key'))
        self.sleep()

        # Test that the displayed API token is the correct one.
        api_token_field = self.drv.find_element_by_id('user-api-token')
        api_token = api_token_field.get_attribute('value')
        self.assertNotEqual(api_token, '')

        user_token = get_user_token()
        self.assertTrue(bcrypt_sha256.verify(api_token, user_token))

        # Test that generating a new token invalidates the old one.
        self.click(self.drv.find_element_by_class_name('btn-api-key'))
        self.sleep()
        new_token = api_token_field.get_attribute('value')
        self.assertNotEqual(new_token, '')

        new_user_token = get_user_token()

        self.assertFalse(bcrypt_sha256.verify(api_token, new_user_token))
        self.assertTrue(bcrypt_sha256.verify(new_token, new_user_token))


class TestAdminUser(AdminTest):
    def sleep(self, duration=None):
        super().sleep(duration)

        is_travis = os.environ.get('TRAVIS', 'f').startswith('t')
        if is_travis and not SAUCE_CONNECT:
            time.sleep(3)

    @report_success_status
    def test_user_administration_renders_properly(self):
        self.get('/view/user-administration')

        self.wait_for_element('table#users tbody tr', by=By.CSS_SELECTOR)
        rows = self.drv.find_elements_by_css_selector('table#users tbody tr')
        self.assertEqual(len(rows), 3)

    @report_success_status
    def test_add_user(self):
        self.get('/view/user-administration')

        self.wait_for_element('btn-edit-user', by=By.CLASS_NAME)

        rows = self.drv.find_elements_by_class_name('btn-edit-user')
        self.assertEqual(len(rows), 3)

        self.sleep(1)
        self.click(self.drv.find_element_by_class_name('btn-add-user'))
        self.wait_for_element('user-name')
        (
            self.drv
            .find_element_by_id('user-name')
            .send_keys('new_user')
        )
        (
            self.drv
            .find_element_by_id('user-email')
            .send_keys('new@email.com')
        )
        save_btn = self.drv.find_element_by_class_name('btn-save-user')
        self.sleep()
        save_btn.click()
        self.sleep()

        self.get('/view/user-administration')
        self.sleep()

        rows = self.drv.find_elements_by_css_selector('table#users tbody tr')
        self.assertEqual(len(rows), 4)

    @report_success_status
    def test_edit_user(self):
        self.get('/view/user-administration')

        self.sleep()
        self.wait_for_element(
            'tr.odd:nth-child(3) > td:nth-child(5) > button:nth-child(1)',
            by=By.CSS_SELECTOR
        )
        edit_btn = self.drv.find_element_by_css_selector(
            'tr.odd:nth-child(3) > td:nth-child(5) > button:nth-child(1)'
        )
        self.sleep()
        self.click(edit_btn)
        self.sleep()
        self.wait_for_element('user-name')
        (
            self.drv
            .find_element_by_id('user-name')
            .send_keys('_edit')
        )
        self.click(self.drv.find_element_by_class_name('btn-save-user'))
        self.sleep()

        self.assertEqual(
            (
                self.drv
                .find_element_by_css_selector(
                    'tr.odd:nth-child(3) > td:nth-child(1)'
                ).text
            ),
            'test_user_b_edit'
        )

    @report_success_status
    def test_delete_user(self):
        self.get('/view/user-administration')

        self.wait_for_element('btn-edit-user', by=By.CLASS_NAME)

        existing = self.drv.find_elements_by_class_name('btn-edit-user')
        self.assertEqual(len(existing), 3)

        self.wait_for_element(
            'tr.odd:nth-child(3) > td:nth-child(5) > button:nth-child(1)',
            by=By.CSS_SELECTOR
        )
        edit_btn = self.drv.find_element_by_css_selector(
            'tr.odd:nth-child(3) > td:nth-child(5) > button:nth-child(1)'
        )
        self.sleep()
        self.click(edit_btn)
        self.sleep()
        self.sleep(1)
        self.wait_for_element('btn-delete-user', by=By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('btn-delete-user'))
        self.sleep()
        alert = self.drv.switch_to.alert
        self.sleep()
        alert.accept()
        self.sleep(1)

        self.get('/view/user-administration')

        self.wait_for_element('btn-edit-user', by=By.CLASS_NAME)
        rows = self.drv.find_elements_by_class_name('btn-edit-user')
        self.assertEqual(len(rows), 2)


class TestAdminManageSurvey(AdminTest):
    @report_success_status
    def test_manage_renders_properly(self):
        self.get('/view/b0816b52-204f-41d4-aaf0-ac6ae2970923')

        # Stats view
        stats = self.drv.find_elements_by_class_name('stat-value')

        self.assertEqual(
            dateutil.parser.parse(stats[0].text).date(),
            datetime.datetime.now().date()
        )
        self.assertEqual(
            dateutil.parser.parse(stats[1].text).date(),
            datetime.datetime.now().date() - datetime.timedelta(days=99)
        )
        self.assertEqual(
            dateutil.parser.parse(stats[2].text).date(),
            datetime.datetime.now().date()
        )
        self.assertEqual(stats[3].text, '101')

        # Enumerate URL
        self.assertEqual(
            (
                self.drv
                .find_element_by_id('shareable-link')
                .get_attribute('value')
            ),
            (
                'http://localhost:9999/enumerate'
                '/b0816b52-204f-41d4-aaf0-ac6ae2970923'
            )
        )

        # Activity graph
        self.assertIsNotNone(
            self.drv.find_element_by_css_selector('path:nth-child(30)')
        )

        # Submissions table
        rows = (
            self.drv
            .find_elements_by_css_selector('table#submissions tbody tr')
        )
        self.assertEqual(len(rows), 5)

    @report_success_status
    def test_download_json_button(self):
        self.get('/view/b0816b52-204f-41d4-aaf0-ac6ae2970923')

        self.click(self.drv.find_element_by_class_name('btn-sm'))
        self.click(self.drv.find_element_by_css_selector(
            '.btn-group > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)'
        ))

        self.switch_window()
        response = BeautifulSoup(self.drv.page_source, 'html.parser')
        json_str = response.find('pre').text
        data = json.loads(json_str)

        self.assertEqual(data['total_entries'], 101)
        self.assertEqual(data['total_entries'], 101)
        self.assertEqual(len(data['submissions']), 101)

    @report_success_status
    def test_download_csv_button(self):
        self.get('/view/b0816b52-204f-41d4-aaf0-ac6ae2970923')

        self.click(self.drv.find_element_by_class_name('btn-sm'))

        json_button = self.drv.find_element_by_css_selector(
            '.btn-group > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)'
        )
        csv_button = self.drv.find_element_by_css_selector(
            '.btn-group > ul:nth-child(2) > li:nth-child(2) > a:nth-child(1)'
        )

        self.assertEqual(
            json_button.get_attribute('href') + '?format=csv',
            csv_button.get_attribute('href')
        )

    @report_success_status
    def test_submission_details_button(self):
        self.get('/view/b0816b52-204f-41d4-aaf0-ac6ae2970923')

        self.click(self.drv.find_element_by_css_selector(
            'tr.odd:nth-child(1) > td:nth-child(4) > button:nth-child(1)'
        ))

        self.wait_for_element('response-data', by=By.CLASS_NAME)
        self.assertEqual(
            self.drv.find_element_by_class_name('response-data').text,
            '3'
        )


class TestAdminViewData(AdminTest):
    @report_success_status
    def test_view_data_renders_properly(self):
        self.get('/view/data/b0816b52-204f-41d4-aaf0-ac6ae2970923')
        self.sleep()

        # Stats view
        stats = self.drv.find_elements_by_class_name('stat-value')

        self.assertEqual(
            dateutil.parser.parse(stats[0].text).date(),
            datetime.datetime.now().date()
        )
        self.assertEqual(
            dateutil.parser.parse(stats[1].text).date(),
            datetime.datetime.now().date() - datetime.timedelta(days=99)
        )
        self.assertEqual(
            dateutil.parser.parse(stats[2].text).date(),
            datetime.datetime.now().date()
        )
        self.assertEqual(stats[3].text, '101')

        # Question data
        self.wait_for_element('question-title-bar', by=By.CLASS_NAME)
        titles = self.drv.find_elements_by_class_name('question-title-bar')
        self.assertListEqual(
            [q.text for q in titles],
            [
                '0. integer node\nINTEGER',
                '1. decimal node\nDECIMAL',
                '2. integer node\nINTEGER',
                '3. date node\nDATE',
                '4. Mutliple Choices\nMULTIPLE_CHOICE',
            ]
        )

        self.click(titles[0])
        q0_stats = self.drv.find_elements_by_class_name('stat-value')[4:12]
        self.assertListEqual(
            [s.text for s in q0_stats],
            ['1', '3', '3', '3', '3.0000000000000000', '3', '0', 'None']
        )


class TestEnumerate(DriverTest):
    def get_single_node_survey_id(self, question_type):
        title = question_type + '_survey'
        return (
            self.session
            .query(Survey.id)
            .filter(Survey.title['English'].astext == title)
            .scalar()
        )

    def get_last_submission(self, survey_id):
        self.sleep()
        return (
            self.session
            .query(Submission)
            .filter_by(survey_id=survey_id)
            .order_by(Submission.save_time.desc())
            .limit(1)
            .one()
        )

    @report_success_status
    def test_single_integer_question(self):
        survey_id = self.get_single_node_survey_id('integer')
        existing_submission = self.get_last_submission(survey_id)

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertIsNot(existing_submission, new_submission)
        self.assertEqual(new_submission.answers[0].answer, 3)
        self.assertIsNotNone(new_submission.start_time)
        self.assertNotEqual(
            new_submission.start_time, new_submission.save_time
        )

    @report_success_status
    def test_previous_and_next(self):
        survey_id = self.get_single_node_survey_id('integer')

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3')
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.assertEqual(
            self.drv.find_element_by_tag_name('input').get_attribute('value'),
            '3'
        )

    @report_success_status
    def test_dont_know(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'allow multiple'},
                nodes=[
                    construct_survey_node(
                        allow_dont_know=True,
                        node=construct_node(
                            title={'English': 'am_integer'},
                            type_constraint='integer',
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.click(self.drv.find_element_by_tag_name('label'))
        (
            self.drv
            .find_elements_by_tag_name('input')[-1]
            .send_keys("Don't know reason")
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(
            new_submission.answers[0].dont_know,
            "Don't know reason"
        )

    @report_success_status
    def test_single_integer_question_bad_input(self):
        survey_id = self.get_single_node_survey_id('integer')

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('so not an integer')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        # No submit button.
        self.assertEqual(
            len(self.drv.find_elements_by_tag_name('button')),
            1
        )

    @report_success_status
    def test_single_decimal_question(self):
        survey_id = self.get_single_node_survey_id('decimal')
        existing_submission = self.get_last_submission(survey_id)

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3.3')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertIsNot(existing_submission, new_submission)
        self.assertEqual(new_submission.answers[0].answer, Decimal('3.3'))

    @report_success_status
    def test_single_decimal_question_bad_input(self):
        survey_id = self.get_single_node_survey_id('decimal')

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3.3.3')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        # No submit button.
        self.assertEqual(
            len(self.drv.find_elements_by_tag_name('button')),
            1
        )

    @report_success_status
    def test_single_text_question(self):
        survey_id = self.get_single_node_survey_id('text')
        existing_submission = self.get_last_submission(survey_id)

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('some text')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertIsNot(existing_submission, new_submission)
        self.assertEqual(new_submission.answers[0].answer, 'some text')

    @report_success_status
    def test_single_photo_question(self):
        survey_id = self.get_single_node_survey_id('photo')
        existing_submission = self.get_last_submission(survey_id)

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.wait_for_element('video', by=By.TAG_NAME, visible=True)
        self.sleep(2)
        self.click(self.drv.find_element_by_tag_name('video'))
        self.sleep(2)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        self.sleep(3)

        new_submission = self.get_last_submission(survey_id)

        self.assertIsNot(existing_submission, new_submission)
        answer = new_submission.answers[0]
        response = answer.response
        self.assertIsNotNone(response['response'])
        self.assertIs(type(response['response']), str)

        photo = self.session.query(Photo).filter_by(id=answer.answer).one()
        self.assertIsNotNone(photo)

    @report_success_status
    def test_single_date_question(self):
        survey_id = self.get_single_node_survey_id('date')
        existing_submission = self.get_last_submission(survey_id)

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.enter_date(
            self.drv.find_element_by_tag_name('input'),
            '2015', '08', '11'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertIsNot(existing_submission, new_submission)
        self.assertEqual(
            new_submission.answers[0].answer.isoformat(),
            '2015-08-11'
        )

    @report_success_status
    def test_single_time_question(self):
        survey_id = self.get_single_node_survey_id('time')
        existing_submission = self.get_last_submission(survey_id)

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.enter_time(
            self.drv.find_element_by_tag_name('input'),
            '3', '33', 'PM'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertIsNot(existing_submission, new_submission)
        answer = new_submission.answers[0].answer.isoformat()
        answer_parts = re.split('[-+]', answer)
        self.assertEqual(len(answer_parts), 2)
        self.assertEqual(answer_parts[0], '15:33:00')

    @report_success_status
    def test_single_timestamp_question(self):
        survey_id = self.get_single_node_survey_id('timestamp')
        existing_submission = self.get_last_submission(survey_id)

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.enter_timestamp(
            self.drv.find_element_by_tag_name('input'),
            '2015', '08', '11', '3', '33', 'PM'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertIsNot(existing_submission, new_submission)
        answer = new_submission.answers[0].answer
        date_answer = answer.date()
        self.assertEqual(date_answer.isoformat(), '2015-08-11')
        time_answer = answer.timetz()
        answer_parts = re.split('[-+]', time_answer.isoformat())
        self.assertEqual(len(answer_parts), 2, msg=answer_parts)
        self.assertEqual(answer_parts[0], '15:33:00')

    @report_success_status
    def test_single_location_question(self):
        survey_id = self.get_single_node_survey_id('location')
        existing_submission = self.get_last_submission(survey_id)

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.set_geolocation()
        self.click(
            self.drv
            .find_element_by_css_selector(
                '.content > span:nth-child(2) > div:nth-child(1)'
                ' > button:nth-child(1)'
            )
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertIsNot(existing_submission, new_submission)
        self.assertEqual(
            new_submission.answers[0].response['response'],
            {'lat': 40, 'lng': -70}
        )

    @report_success_status
    def test_single_facility_question(self):
        survey_id = self.get_single_node_survey_id('facility')
        existing_submission = self.get_last_submission(survey_id)

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.set_geolocation()
        self.click(
            self.drv
            .find_element_by_css_selector(
                '.content > span:nth-child(2) > span:nth-child(1)'
                ' > div:nth-child(1) > button:nth-child(1)'
            )
        )
        self.sleep(2)
        self.click(
            self.drv
            .find_elements_by_class_name('question__radio__label')[0]
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertIsNot(existing_submission, new_submission)
        self.assertEqual(
            new_submission.answers[0].response['response']['facility_name'],
            'Queensborough Community College - City University of New York'
        )

    @report_success_status
    def test_offline_facility_tree(self):
        survey_id = self.get_single_node_survey_id('facility')
        existing_submission = self.get_last_submission(survey_id)

        self.get('/enumerate/{}'.format(survey_id))

        self.toggle_online()

        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.set_geolocation()
        self.click(
            self.drv
            .find_element_by_css_selector(
                '.content > span:nth-child(2) > span:nth-child(1)'
                ' > div:nth-child(1) > button:nth-child(1)'
            )
        )
        self.sleep()
        self.wait_for_element('question__radio__label', by=By.CLASS_NAME)
        self.click(
            self.drv
            .find_elements_by_class_name('question__radio__label')[0]
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.toggle_online(revisit=False)

        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertIsNot(existing_submission, new_submission)
        self.assertEqual(
            new_submission.answers[0].response['response']['facility_name'],
            'Queensborough Community College - City University of New York'
        )

    @report_success_status
    def test_single_multiple_choice_question(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'allow multiple'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'other_mc'},
                            type_constraint='multiple_choice',
                            choices=[
                                Choice(choice_text={'English': 'one'}),
                                Choice(choice_text={'English': 'two'}),
                            ],
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.click(self.drv.find_elements_by_tag_name('option')[1])

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(
            new_submission.answers[0].choice.choice_text,
            {'English': 'one'}
        )

    @report_success_status
    def test_select_multiple(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'allow multiple'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'other_mc'},
                            type_constraint='multiple_choice',
                            allow_multiple=True,
                            choices=[
                                Choice(choice_text={'English': 'one'}),
                                Choice(choice_text={'English': 'two'}),
                            ],
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.click(self.drv.find_elements_by_tag_name('option')[1])
        self.click(self.drv.find_elements_by_tag_name('option')[2])

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(
            new_submission.answers[0].choice.choice_text,
            {'English': 'one'}
        )
        self.assertEqual(
            new_submission.answers[1].choice.choice_text,
            {'English': 'two'}
        )

    @report_success_status
    def test_other(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'allow multiple'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'other_mc'},
                            type_constraint='multiple_choice',
                            choices=[
                                Choice(choice_text={'English': 'one'}),
                                Choice(choice_text={'English': 'two'}),
                            ],
                            allow_other=True,
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.click(self.drv.find_elements_by_tag_name('option')[-1])
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('other choice not listed')
        )

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(
            new_submission.answers[0].other,
            'other choice not listed'
        )

    @report_success_status
    def test_connectivity_cuts_out(self):
        survey_id = self.get_single_node_survey_id('integer')
        existing_submission = self.get_last_submission(survey_id)

        self.get('/enumerate/{}'.format(survey_id))

        self.toggle_online()

        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.toggle_online()
        time.sleep(1)

        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertIsNot(existing_submission, new_submission)
        self.assertEqual(new_submission.answers[0].answer, 3)

    @report_success_status
    def test_offline_no_submit_button(self):
        survey_id = self.get_single_node_survey_id('integer')

        self.get('/enumerate/{}'.format(survey_id))

        self.toggle_online()

        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.assertEqual(len(self.drv.find_elements_by_tag_name('button')), 1)

    @report_success_status
    def test_presence_of_submit_button(self):
        survey_id = self.get_single_node_survey_id('integer')

        self.get('/enumerate/{}'.format(survey_id))

        self.toggle_online()

        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.assertEqual(len(self.drv.find_elements_by_tag_name('button')), 1)

        self.toggle_online()
        time.sleep(1)
        self.assertEqual(len(self.drv.find_elements_by_tag_name('button')), 2)

        self.toggle_online()
        time.sleep(1)
        self.assertEqual(len(self.drv.find_elements_by_tag_name('button')), 1)

    @report_success_status
    def test_offline_work_is_saved(self):
        survey_id = self.get_single_node_survey_id('integer')
        existing_submission = self.get_last_submission(survey_id)

        enumerate_url = '/enumerate/{}'.format(survey_id)
        self.get(enumerate_url)

        self.toggle_online()

        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.drv.get('about:blank')  # unload the page
        self.get(enumerate_url)

        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertIsNot(existing_submission, new_submission)
        self.assertEqual(new_submission.answers[0].answer, 3)

    @report_success_status
    def test_allow_multiple(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'allow multiple'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'am_integer'},
                            type_constraint='integer',
                            allow_multiple=True,
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3')
        )
        self.click(
            self.drv
            .find_element_by_css_selector(
                'div.content-padded:last-child > button:nth-child(1)'
            )
        )
        (
            self.drv
            .find_elements_by_tag_name('input')[-1]
            .send_keys('4')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        time.sleep(1)

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(new_submission.answers[0].answer, 3)
        self.assertEqual(new_submission.answers[1].answer, 4)

    @report_success_status
    def test_allow_multiple_remove_an_answer(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'allow multiple'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'am_integer'},
                            type_constraint='integer',
                            allow_multiple=True,
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3')
        )
        self.click(
            self.drv
            .find_element_by_css_selector(
                'div.content-padded:last-child > button:nth-child(1)'
            )
        )
        (
            self.drv
            .find_elements_by_tag_name('input')[-1]
            .send_keys('4')
        )
        self.click(
            self.drv
            .find_element_by_css_selector(
                'div.content-padded:last-child > button:nth-child(1)'
            )
        )
        (
            self.drv
            .find_elements_by_tag_name('input')[-1]
            .send_keys('5')
        )
        self.click(
            self.drv
            .find_element_by_css_selector(
                'div.input_container:nth-child(2) > span:nth-child(2)'
            )
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(new_submission.answers[0].answer, 3)
        self.assertEqual(new_submission.answers[1].answer, 5)

    @report_success_status
    def test_allow_multiple_bad_input(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'allow multiple'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'am_integer'},
                            type_constraint='integer',
                            allow_multiple=True,
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3')
        )
        self.click(
            self.drv
            .find_element_by_css_selector(
                'div.content-padded:last-child > button:nth-child(1)'
            )
        )
        (
            self.drv
            .find_elements_by_tag_name('input')[-1]
            .send_keys('not an integer')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(new_submission.answers[0].answer, 3)
        self.assertEqual(len(new_submission.answers), 1)

    @report_success_status
    def test_required_question_no_answer(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        node = (
            self.session
            .query(Node)
            .filter(Node.title['English'].astext == 'integer_node')
            .one()
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'required question'},
                nodes=[
                    construct_survey_node(
                        required=True,
                        node=node,
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        # Try to move on without answering the question
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        # An alert pops up
        # TODO: change this behavior
        alert = self.drv.switch_to.alert
        alert.accept()

        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(new_submission.answers[0].answer, 3)

    @report_success_status
    def test_required_question_bad_answer(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        node = (
            self.session
            .query(Node)
            .filter(Node.title['English'].astext == 'integer_node')
            .one()
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'required question'},
                nodes=[
                    construct_survey_node(
                        required=True,
                        node=node,
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('not an integer')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        # An alert pops up
        # TODO: change this behavior
        alert = self.drv.switch_to.alert
        alert.accept()

        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('3')
            .perform()
        )

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(new_submission.answers[0].answer, 3)

    @report_success_status
    def test_allow_multiple_cant_fool_required(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'allow multiple'},
                nodes=[
                    construct_survey_node(
                        required=True,
                        node=construct_node(
                            title={'English': 'am_integer'},
                            type_constraint='integer',
                            allow_multiple=True,
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3')
        )
        self.click(
            self.drv
            .find_element_by_css_selector(
                'div.content-padded:last-child > button:nth-child(1)'
            )
        )
        (
            self.drv
            .find_elements_by_tag_name('input')[-1]
            .send_keys('not an integer')
        )
        (
            self.drv
            .find_elements_by_tag_name('input')[0]
            .send_keys('not an integer')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        # An alert pops up
        # TODO: change this behavior
        alert = self.drv.switch_to.alert
        alert.accept()

        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_elements_by_tag_name('input')[0]
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('3')
            .perform()
        )
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_elements_by_tag_name('input')[-1]
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('4')
            .perform()
        )

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(new_submission.answers[0].answer, 3)
        self.assertEqual(new_submission.answers[1].answer, 4)

    @report_success_status
    def test_basic_branching(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'basic branching'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'integer_0'},
                            type_constraint='integer',
                        ),
                    ),
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'integer_1'},
                            type_constraint='integer',
                        ),
                        sub_surveys=[
                            SubSurvey(
                                buckets=[
                                    construct_bucket(
                                        bucket_type='integer',
                                        bucket='[10,20]',
                                    ),
                                ],
                                nodes=[
                                    construct_survey_node(
                                        node=construct_node(
                                            title={
                                                'English': 'branch',
                                            },
                                            type_constraint='text',
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'integer_2'},
                            type_constraint='integer',
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('15')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'branch'
        )

        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('in a branch')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('4')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(new_submission.answers[0].answer, 3)
        self.assertEqual(new_submission.answers[1].answer, 15)
        self.assertEqual(new_submission.answers[2].answer, 'in a branch')
        self.assertEqual(new_submission.answers[3].answer, 4)

    @report_success_status
    def test_first_question_branching(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'basic branching'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'integer_0'},
                            type_constraint='integer',
                        ),
                        sub_surveys=[
                            SubSurvey(
                                buckets=[
                                    construct_bucket(
                                        bucket_type='integer',
                                        bucket='[10,20]',
                                    ),
                                ],
                                nodes=[
                                    construct_survey_node(
                                        node=construct_node(
                                            title={
                                                'English': 'branch',
                                            },
                                            type_constraint='text',
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'integer_1'},
                            type_constraint='integer',
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('15')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'branch'
        )

        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('in a branch')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('4')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(new_submission.answers[0].answer, 15)
        self.assertEqual(new_submission.answers[1].answer, 'in a branch')
        self.assertEqual(new_submission.answers[2].answer, 4)

    @report_success_status
    def test_last_question_branching_enter_branch(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'basic branching'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'integer_0'},
                            type_constraint='integer',
                        ),
                    ),
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'integer_1'},
                            type_constraint='integer',
                        ),
                        sub_surveys=[
                            SubSurvey(
                                buckets=[
                                    construct_bucket(
                                        bucket_type='integer',
                                        bucket='[10,20]',
                                    ),
                                ],
                                nodes=[
                                    construct_survey_node(
                                        node=construct_node(
                                            title={
                                                'English': 'branch',
                                            },
                                            type_constraint='text',
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('4')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('15')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'branch'
        )

        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('in a branch')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(new_submission.answers[0].answer, 4)
        self.assertEqual(new_submission.answers[1].answer, 15)
        self.assertEqual(new_submission.answers[2].answer, 'in a branch')

    @report_success_status
    def test_last_question_branching_do_not_enter_branch(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'basic branching'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'integer_0'},
                            type_constraint='integer',
                        ),
                    ),
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'integer_1'},
                            type_constraint='integer',
                        ),
                        sub_surveys=[
                            SubSurvey(
                                buckets=[
                                    construct_bucket(
                                        bucket_type='integer',
                                        bucket='[10,20]',
                                    ),
                                ],
                                nodes=[
                                    construct_survey_node(
                                        node=construct_node(
                                            title={
                                                'English': 'branch',
                                            },
                                            type_constraint='text',
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('4')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('25')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.assertNotEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'branch'
        )

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(new_submission.answers[0].answer, 4)
        self.assertEqual(new_submission.answers[1].answer, 25)

    @report_success_status
    def test_branch_nesting(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'basic branching'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'integer_0'},
                            type_constraint='integer',
                        ),
                        sub_surveys=[
                            SubSurvey(
                                buckets=[
                                    construct_bucket(
                                        bucket_type='integer',
                                        bucket='[10,20]',
                                    ),
                                ],
                                nodes=[
                                    construct_survey_node(
                                        node=construct_node(
                                            title={
                                                'English': 'branch_0',
                                            },
                                            type_constraint='text',
                                        ),
                                    ),
                                ],
                            ),
                            SubSurvey(
                                buckets=[
                                    construct_bucket(
                                        bucket_type='integer',
                                        bucket='[21,30]',
                                    ),
                                ],
                                nodes=[
                                    construct_survey_node(
                                        node=construct_node(
                                            title={
                                                'English': 'branch_1',
                                            },
                                            type_constraint='integer',
                                        ),
                                        sub_surveys=[
                                            SubSurvey(
                                                buckets=[
                                                    construct_bucket(
                                                        bucket_type='integer',
                                                        bucket='[10,20]',
                                                    ),
                                                ],
                                                nodes=[
                                                    construct_survey_node(
                                                        node=construct_node(
                                                            title={
                                                                'English': (
                                                                    'branch_2'
                                                                ),
                                                            },
                                                            type_constraint=(
                                                                'text'
                                                            ),
                                                        ),
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'integer_1'},
                            type_constraint='integer',
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('25')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'branch_1'
        )

        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('15')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'branch_2'
        )

        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('do not submit this')
        )

        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))

        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'integer_0'
        )

        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('15')
            .perform()
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'branch_0'
        )

        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('submit this')
        )

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(len(new_submission.answers), 3)
        self.assertEqual(new_submission.answers[0].answer, 15)
        self.assertEqual(new_submission.answers[1].answer, 'submit this')
        self.assertEqual(new_submission.answers[2].answer, 3)

    @report_success_status
    def test_nesting_maintains_answers(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'basic branching'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'integer_0'},
                            type_constraint='integer',
                        ),
                        sub_surveys=[
                            SubSurvey(
                                buckets=[
                                    construct_bucket(
                                        bucket_type='integer',
                                        bucket='[10,20]',
                                    ),
                                ],
                                nodes=[
                                    construct_survey_node(
                                        node=construct_node(
                                            title={
                                                'English': 'branch_0',
                                            },
                                            type_constraint='integer',
                                        ),
                                        sub_surveys=[
                                            SubSurvey(
                                                buckets=[
                                                    construct_bucket(
                                                        bucket_type='integer',
                                                        bucket='[10,20]',
                                                    ),
                                                ],
                                                nodes=[
                                                    construct_survey_node(
                                                        node=construct_node(
                                                            title={
                                                                'English': (
                                                                    'branch_2'
                                                                ),
                                                            },
                                                            type_constraint=(
                                                                'text'
                                                            ),
                                                        ),
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'integer_1'},
                            type_constraint='integer',
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('15')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('16')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('submit this')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3')
        )

        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))

        self.assertEqual(
            self.drv.find_element_by_tag_name('input').get_attribute('value'),
            '15'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('input').get_attribute('value'),
            '16'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('input').get_attribute('value'),
            'submit this'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('input').get_attribute('value'),
            '3'
        )

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertEqual(len(new_submission.answers), 4)
        self.assertEqual(new_submission.answers[0].answer, 15)
        self.assertEqual(new_submission.answers[1].answer, 16)
        self.assertEqual(new_submission.answers[2].answer, 'submit this')
        self.assertEqual(new_submission.answers[3].answer, 3)

    @report_success_status
    def test_multiple_buckets_for_same_branch(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'basic branching'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'branching'},
                            type_constraint='integer',
                        ),
                        sub_surveys=[
                            SubSurvey(
                                buckets=[
                                    construct_bucket(
                                        bucket_type='integer',
                                        bucket='[0, 10]',
                                    ),
                                    construct_bucket(
                                        bucket_type='integer',
                                        bucket='[20, 30]',
                                    ),
                                ],
                                nodes=[
                                    construct_survey_node(
                                        node=construct_node(
                                            title={'English': 'branch'},
                                            type_constraint='text',
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'last question'},
                            type_constraint='integer',
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('5')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'branch'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('25')
            .perform()
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'branch'
        )

    def survey_with_branch(self, type_constraint, *buckets):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'basic branching'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'branching'},
                            type_constraint=type_constraint,
                        ),
                        sub_surveys=[
                            SubSurvey(
                                buckets=[
                                    construct_bucket(
                                        bucket_type=type_constraint,
                                        bucket=bucket,
                                    ),
                                ],
                                nodes=[
                                    construct_survey_node(
                                        node=construct_node(
                                            title={'English': 'b{}'.format(i)},
                                            type_constraint='text',
                                        ),
                                    ),
                                ],
                            ) for i, bucket in enumerate(buckets)
                        ],
                    ),
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'last question'},
                            type_constraint='integer',
                        ),
                    ),
                ],
            )
            self.session.add(survey)
        return survey.id

    @report_success_status
    def test_integer_buckets(self):
        survey_id = self.survey_with_branch('integer', '(1, 3)', '[4, 5]')

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('2')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('4')
            .perform()
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b1'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('1')
            .perform()
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'last question'
        )

    @report_success_status
    def test_integer_buckets_open_ranges(self):
        survey_id = self.survey_with_branch('integer', '(, 0)', '[10,)')

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('-5')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('15')
            .perform()
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b1'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('5')
            .perform()
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'last question'
        )

    @report_success_status
    def test_integer_buckets_total_open(self):
        survey_id = self.survey_with_branch('integer', '(,)')

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('-999')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('999')
            .perform()
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )

    @report_success_status
    def test_decimal_buckets(self):
        survey_id = self.survey_with_branch(
            'decimal',
            '(1.2, 3.2)',
            '[4.2, 5.2]'
        )

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('1.3')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('4.2')
            .perform()
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b1'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('1.2')
            .perform()
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'last question'
        )

    @report_success_status
    def test_decimal_buckets_open_ranges(self):
        survey_id = self.survey_with_branch('decimal', '(, 0.1)', '[10.1,)')

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('-5.1')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('15.1')
            .perform()
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b1'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('5.1')
            .perform()
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'last question'
        )

    @report_success_status
    def test_decimal_buckets_total_open(self):
        survey_id = self.survey_with_branch('decimal', '(,)')

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('-999.1')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('999.1')
            .perform()
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )

    @report_success_status
    def test_date_buckets(self):
        survey_id = self.survey_with_branch(
            'date',
            '(2015-01-01, 2015-01-03)',
            '[2015-01-04, 2015-01-05]'
        )

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.enter_date(
            self.drv.find_element_by_tag_name('input'),
            '2015', '01', '02'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys(Keys.DELETE)
            .perform()
        )
        self.enter_date(
            self.drv.find_element_by_tag_name('input'),
            '2015', '01', '04'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b1'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys(Keys.DELETE)
            .perform()
        )
        self.enter_date(
            self.drv.find_element_by_tag_name('input'),
            '2015', '01', '01'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'last question'
        )

    @report_success_status
    def test_date_buckets_open_ranges(self):
        survey_id = self.survey_with_branch(
            'date',
            '(, 2015-01-01)',
            '[2015-01-10,]'
        )

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.enter_date(
            self.drv.find_element_by_tag_name('input'),
            '2014', '11', '22'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys(Keys.DELETE)
            .perform()
        )
        self.enter_date(
            self.drv.find_element_by_tag_name('input'),
            '2015', '11', '22'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b1'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys(Keys.DELETE)
            .perform()
        )
        self.enter_date(
            self.drv.find_element_by_tag_name('input'),
            '2015', '01', '05'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'last question'
        )

    @report_success_status
    def test_date_buckets_total_open(self):
        survey_id = self.survey_with_branch('date', '(,)')

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.enter_date(
            self.drv.find_element_by_tag_name('input'),
            '1970', '01', '05'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys(Keys.DELETE)
            .perform()
        )
        self.enter_date(
            self.drv.find_element_by_tag_name('input'),
            '2070', '01', '05'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )

    @report_success_status
    def test_timestamp_buckets(self):
        survey_id = self.survey_with_branch(
            'timestamp',
            '(2015-01-01T1:00:00Z, 2015-01-03:1:00:00Z)',
            '[2015-01-04T1:00:00Z, 2015-01-05T1:00:00Z]'
        )

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.enter_timestamp_temporary(
            self.drv.find_element_by_tag_name('input'),
            '2015', '01', '02', '01', '00', 'AM'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys(Keys.DELETE)
            .perform()
        )
        self.enter_timestamp_temporary(
            self.drv.find_element_by_tag_name('input'),
            '2015', '01', '04', '01', '00', 'AM'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b1'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys(Keys.DELETE)
            .perform()
        )
        self.enter_timestamp_temporary(
            self.drv.find_element_by_tag_name('input'),
            '2015', '01', '01', '01', '00', 'AM'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'last question'
        )

    @report_success_status
    def test_timestamp_buckets_open_ranges(self):
        survey_id = self.survey_with_branch(
            'timestamp',
            '(, 2015-01-01T1:00:00Z)',
            '[2015-01-10T1:00:00Z,]'
        )

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.enter_timestamp(
            self.drv.find_element_by_tag_name('input'),
            '2014', '11', '22', '01', '00', 'AM'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys(Keys.DELETE)
            .perform()
        )
        self.enter_timestamp(
            self.drv.find_element_by_tag_name('input'),
            '2015', '11', '22', '01', '00', 'AM'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b1'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys(Keys.DELETE)
            .perform()
        )
        self.enter_timestamp(
            self.drv.find_element_by_tag_name('input'),
            '2015', '01', '05', '01', '00', 'AM'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'last question'
        )

    @report_success_status
    def test_timestamp_buckets_total_open(self):
        survey_id = self.survey_with_branch('timestamp', '(,)')

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.enter_timestamp(
            self.drv.find_element_by_tag_name('input'),
            '1970', '01', '05', '01', '00', 'AM'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys(Keys.DELETE)
            .perform()
        )
        self.enter_timestamp(
            self.drv.find_element_by_tag_name('input'),
            '2070', '01', '05', '01', '00', 'AM'
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )

    @report_success_status
    def test_multiple_choice_buckets(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            node = construct_node(
                title={'English': 'branching'},
                type_constraint='multiple_choice',
                choices=[
                    Choice(
                        choice_text={'English': str(i)}
                    ) for i in range(3)
                ],
            )
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'basic branching'},
                nodes=[
                    construct_survey_node(
                        node=node,
                        sub_surveys=[
                            SubSurvey(
                                buckets=[
                                    construct_bucket(
                                        bucket_type='multiple_choice',
                                        bucket=choice,
                                    ),
                                ],
                                nodes=[
                                    construct_survey_node(
                                        node=construct_node(
                                            title={'English': 'b{}'.format(i)},
                                            type_constraint='text',
                                        ),
                                    ),
                                ],
                            ) for i, choice in enumerate(node.choices[:2])
                        ],
                    ),
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'last question'},
                            type_constraint='integer',
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('option')[1])
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b0'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        self.click(self.drv.find_elements_by_tag_name('option')[2])
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'b1'
        )
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))
        self.click(self.drv.find_elements_by_tag_name('option')[3])
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'last question'
        )

    @report_success_status
    def test_after_saving_branch_path_resets(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            node = construct_node(
                title={'English': 'branching'},
                type_constraint='integer',
            )
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'basic branching'},
                nodes=[
                    construct_survey_node(
                        node=node,
                        sub_surveys=[
                            SubSurvey(
                                buckets=[
                                    construct_bucket(
                                        bucket_type='integer',
                                        bucket='[0, 10]',
                                    ),
                                ],
                                nodes=[
                                    construct_survey_node(
                                        node=construct_node(
                                            title={'English': 'begin nesting'},
                                            type_constraint='integer',
                                        ),
                                        sub_surveys=[
                                            SubSurvey(
                                                buckets=[
                                                    construct_bucket(
                                                        bucket_type='integer',
                                                        bucket='[20, 30]',
                                                    ),
                                                ],
                                                nodes=[
                                                    construct_survey_node(
                                                        node=construct_node(
                                                            title={
                                                                'English': (
                                                                    'nest 2'
                                                                ),
                                                            },
                                                            type_constraint=(
                                                                'text'
                                                            ),
                                                        ),
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'last question'},
                            type_constraint='integer',
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('5')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('25')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('save this')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('4')
        )
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.assertEqual(
            self.drv.find_element_by_tag_name('h3').text,
            'last question'
        )

    @report_success_status
    def test_logic_integer_min_max(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'integer logic'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'integer question'},
                            type_constraint='integer',
                            logic={'min': 5, 'max': 10},
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('7')
        )

        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:invalid')),
            0
        )
        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:valid')),
            1
        )

        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('2')
            .perform()
        )

        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:invalid')),
            1
        )
        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:valid')),
            0
        )

        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('12')
            .perform()
        )

        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:invalid')),
            1
        )
        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:valid')),
            0
        )

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.assertEqual(len(self.drv.find_elements_by_tag_name('button')), 1)

    @report_success_status
    def test_logic_decimal_min_max(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'decimal logic'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'decimal question'},
                            type_constraint='decimal',
                            logic={'min': 5.0, 'max': 10.0},
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('7')
        )

        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:invalid')),
            0
        )
        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:valid')),
            1
        )

        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('2')
            .perform()
        )

        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:invalid')),
            1
        )
        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:valid')),
            0
        )

        (
            ActionChains(self.drv)
            .key_down(
                self.control_key,
                self.drv.find_element_by_tag_name('input')
            )
            .send_keys('a')
            .key_up(self.control_key)
            .send_keys('12')
            .perform()
        )

        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:invalid')),
            1
        )
        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:valid')),
            0
        )

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.assertEqual(len(self.drv.find_elements_by_tag_name('button')), 1)

    @report_success_status
    def test_logic_date_min_max(self):
        user = (
            self.session
            .query(Administrator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            survey = construct_survey(
                creator=user,
                survey_type='public',
                title={'English': 'date logic'},
                nodes=[
                    construct_survey_node(
                        node=construct_node(
                            title={'English': 'date question'},
                            type_constraint='date',
                            logic={'min': '2015-09-05', 'max': '2015-09-10'},
                        ),
                    ),
                ],
            )
            self.session.add(survey)

        survey_id = survey.id

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.enter_date(
            self.drv.find_element_by_tag_name('input'),
            '2015', '09', '07'
        )

        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:invalid')),
            0
        )
        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:valid')),
            1
        )

        # For some reason the Ctrl+A approach doesn't work on Chrome...
        if self.browser == 'chrome':
            (
                self.drv
                .find_element_by_tag_name('input')
                .send_keys(Keys.LEFT, Keys.LEFT)
            )
        else:
            (
                ActionChains(self.drv)
                .key_down(
                    self.control_key,
                    self.drv.find_element_by_tag_name('input')
                )
                .send_keys('a')
                .key_up(self.control_key)
                .send_keys(Keys.DELETE)
                .perform()
            )
        self.enter_date(
            self.drv.find_element_by_tag_name('input'),
            '2015', '09', '02'
        )

        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:invalid')),
            1
        )
        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:valid')),
            0
        )

        if self.browser == 'chrome':
            (
                self.drv
                .find_element_by_tag_name('input')
                .send_keys(Keys.LEFT, Keys.LEFT)
            )
        else:
            (
                ActionChains(self.drv)
                .key_down(
                    self.control_key,
                    self.drv.find_element_by_tag_name('input')
                )
                .send_keys('a')
                .key_up(self.control_key)
                .send_keys(Keys.DELETE)
                .perform()
            )
        self.enter_date(
            self.drv.find_element_by_tag_name('input'),
            '2015', '09', '12'
        )

        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:invalid')),
            1
        )
        self.assertEqual(
            len(self.drv.find_elements_by_css_selector('input:valid')),
            0
        )

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))

        self.assertEqual(len(self.drv.find_elements_by_tag_name('button')), 1)

    @report_success_status
    def test_add_new_facility(self):
        survey_id = self.get_single_node_survey_id('facility')
        existing_submission = self.get_last_submission(survey_id)

        self.get('/enumerate/{}'.format(survey_id))
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.set_geolocation()
        self.click(
            self.drv
            .find_element_by_css_selector(
                '.content > span:nth-child(2) > span:nth-child(1)'
                ' > div:nth-child(1) > button:nth-child(1)'
            )
        )
        self.sleep()
        self.wait_for_element(
            'div.content-padded:nth-child(3) > button:nth-child(1)',
            by=By.CSS_SELECTOR
        )
        self.click(
            self.drv
            .find_element_by_css_selector(
                'div.content-padded:nth-child(3) > button:nth-child(1)'
            )
        )
        (
            self.drv
            .find_elements_by_tag_name('input')[0]
            .send_keys('new facility')
        )
        self.click(self.drv.find_elements_by_tag_name('option')[1])

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertIsNot(existing_submission, new_submission)
        self.assertEqual(
            new_submission.answers[0].response['response']['facility_name'],
            'new facility'
        )

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(
            self.drv
            .find_element_by_css_selector(
                '.content > span:nth-child(2) > span:nth-child(1)'
                ' > div:nth-child(1) > button:nth-child(1)'
            )
        )

        new_facility_text = (
            self.drv
            .find_elements_by_class_name('question__radio__label')[0]
            .text
        )
        self.assertEqual(new_facility_text.split('\n')[0], 'new facility')

    @report_success_status
    def test_add_new_facility_revisit_cuts_out(self):
        survey_id = self.get_single_node_survey_id('facility')
        existing_submission = self.get_last_submission(survey_id)

        self.get('/enumerate/{}'.format(survey_id))
        self.toggle_online(browser=False, revisit=True)
        self.wait_for_element('navigate-right', By.CLASS_NAME)
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.set_geolocation()
        self.click(
            self.drv
            .find_element_by_css_selector(
                '.content > span:nth-child(2) > span:nth-child(1)'
                ' > div:nth-child(1) > button:nth-child(1)'
            )
        )
        self.sleep()
        self.click(
            self.drv
            .find_element_by_css_selector(
                'div.content-padded:nth-child(3) > button:nth-child(1)'
            )
        )
        (
            self.drv
            .find_elements_by_tag_name('input')[0]
            .send_keys('new facility')
        )
        self.click(self.drv.find_elements_by_tag_name('option')[1])

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertIsNot(existing_submission, new_submission)
        self.assertEqual(
            new_submission.answers[0].response['response']['facility_name'],
            'new facility'
        )

        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(
            self.drv
            .find_element_by_css_selector(
                '.content > span:nth-child(2) > span:nth-child(1)'
                ' > div:nth-child(1) > button:nth-child(1)'
            )
        )

        self.wait_for_element('question__radio__label', by=By.CLASS_NAME)
        new_facility_text = (
            self.drv
            .find_elements_by_class_name('question__radio__label')[0]
            .text
        )
        self.assertEqual(new_facility_text.split('\n')[0], 'new facility')
