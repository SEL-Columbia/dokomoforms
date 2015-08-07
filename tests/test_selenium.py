"""Front end tests."""
import base64
from distutils.version import StrictVersion
import functools
import json
from http.client import HTTPConnection
import os
from subprocess import Popen, DEVNULL
import signal
import sys
import unittest
import urllib.error

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import tests.util

import config
SAUCE_CONNECT = getattr(config, 'SAUCE_CONNECT', False)
if not SAUCE_CONNECT:
    SAUCE_CONNECT = os.environ.get('SAUCE_CONNECT', False)
SAUCE_USERNAME = getattr(config, 'SAUCE_USERNAME', None)
SAUCE_ACCESS_KEY = getattr(config, 'SAUCE_ACCESS_KEY', None)
DEFAULT_BROWSER = getattr(config, 'DEFAULT_BROWSER', None)


base = 'http://localhost:9999'
webapp = None


def setUpModule():
    """Start the webapp in the background on port 9999."""
    global webapp
    tests.util.setUpModule()
    webapp = Popen(
        [
            'python', 'webapp.py',
            '--port=9999',
            '--debug=True',
            '--https=False',
            '--persona_verification_url={}/debug/persona_verify'.format(base),
        ],
        stdout=DEVNULL, stderr=DEVNULL, preexec_fn=os.setsid
    )


def kill_webapp():
    """Kill the webapp cleanly."""
    if webapp.stdout:
        webapp.stdout.close()
    if webapp.stderr:
        webapp.stderr.close()
    if webapp.stdin:
        webapp.stdin.close()
    os.killpg(webapp.pid, signal.SIGTERM)


def tearDownModule():
    tests.util.tearDownModule()
    kill_webapp()


def keyboard_interrupt_handler(signal, frame):
    """This handler allows you to hit Ctrl-C without worry."""
    kill_webapp()
    sys.exit()


signal.signal(signal.SIGINT, keyboard_interrupt_handler)


def report_success_status(method):
    @functools.wraps(method)
    def set_passed(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self.passed = True
        return result
    return set_passed


class DriverTest(tests.util.DokoHTTPTest):
    def setUp(self):
        super().setUp()

        self.passed = False

        if not SAUCE_CONNECT:
            self.drv = webdriver.Firefox()
            self.browser = 'Firefox'
            self.platform = 'Linux'
            return

        self.username = os.environ.get('SAUCE_USERAME', SAUCE_USERNAME)
        self.access_key = os.environ.get('SAUCE_ACCESS_KEY', SAUCE_ACCESS_KEY)
        browser_config = os.environ.get('BROWSER', DEFAULT_BROWSER)
        values = (self.username, self.access_key, browser_config)
        if any(v is None for v in values):
            self.fail(
                'You have specified SAUCE_CONNECT = True but you have not'
                ' specified SAUCE_USERNAME, SAUCE_ACCESS_KEY,'
                ' and DEFAULT_BROWSER'
            )
        configs = browser_config.split(':')
        self.browser, self.version, self.platform, *other = configs
        caps = {'browserName': self.browser, 'platform': self.platform}
        if self.browser in {'android': 'iPhone'}:
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
                self.__class__.__name__
            ))
        else:
            caps['name'] = ' -- '.join((
                'Manual run',
                browser_config,
                self.__class__.__name__
            ))
        hub_url = '{}:{}@localhost:4445'.format(self.username, self.access_key)
        cmd_executor = 'http://{}/wd/hub'.format(hub_url)
        try:
            self.drv = webdriver.Remote(
                desired_capabilities=caps, command_executor=cmd_executor
            )
        except urllib.error.URLError:
            self.fail('Sauce Connect failure. Did you start Sauce Connect?')
        self.drv.implicitly_wait(10)

    def _set_sauce_status(self):
        credentials = '{}:{}'.format(self.username, self.access_key).encode()
        auth = base64.encodebytes(credentials)[:-1].decode()
        body = json.dumps({'passed': self.passed})
        connection = HTTPConnection('saucelabs.com')
        path = '/rest/v1/{}/jobs/{}'.format(self.username, self.drv.session_id)
        headers = {'Authorization': 'Basic {}'.format(auth)}
        connection.request('PUT', path, body, headers=headers)

    def tearDown(self):
        super().tearDown()

        self.drv.quit()

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

    def wait_for_element(self, identifier, by=By.ID, timeout=1, visible=False):
        visibility = EC.visibility_of_element_located
        presence = EC.presence_of_element_located
        loader = visibility if visible else presence
        load = loader((by, identifier))
        WebDriverWait(self.drv, timeout).until(load)


class TestAuth(DriverTest):
    @unittest.skipIf(
        (not SAUCE_CONNECT) and (os.environ.get('TRAVIS', 'false') == 'true'),
        'This test just refuses to work with xvfb on Travis.'
    )
    @report_success_status
    def test_login(self):
        self.get('/')
        self.wait_for_element('btn-login', By.CLASS_NAME)
        self.drv.find_elements_by_class_name('btn-login')[-1].click()
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
