"""Front end tests."""
import base64
from decimal import Decimal
from distutils.version import StrictVersion
import functools
import json
from http.client import HTTPConnection
import os
import re
from subprocess import check_output, Popen, STDOUT, DEVNULL, CalledProcessError
import signal
import sys
import time
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
    SAUCE_CONNECT = os.environ.get('SAUCE_CONNECT', 'f').startswith('t')
SAUCE_USERNAME = getattr(config, 'SAUCE_USERNAME', None)
SAUCE_ACCESS_KEY = getattr(config, 'SAUCE_ACCESS_KEY', None)
DEFAULT_BROWSER = getattr(config, 'DEFAULT_BROWSER', None)

from dokomoforms.models import Survey, Submission, Photo


base = 'http://localhost:9999'
webapp = None


def setUpModule():
    """Start the webapp in the background on port 9999."""
    global webapp
    tests.util.setUpModule()
    try:
        already_running = (
            check_output(['lsof', '-t', '-i:9999'], stderr=STDOUT)
            .decode()
            .strip()
        ) is not None
    except CalledProcessError:
        already_running = None
    if not already_running:
        webapp = Popen(
            [
                'python', 'webapp.py',
                '--port=9999',
                '--schema=doko_test',
                '--debug=True',
                '--https=False',
                '--persona_verification_url='
                '{}/debug/persona_verify'.format(base),
                '--revisit_url={}/debug/facilities'.format(base),
            ],
            stdout=DEVNULL, stderr=DEVNULL, preexec_fn=os.setsid
        )
        time.sleep(1)


def kill_webapp():
    """Kill the webapp cleanly."""
    if not webapp:
        return
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
        caps = {'browserName': self.browser, 'platform': self.platform}
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
                self.__class__.__name__
            ))
        hub_url = '{}:{}@localhost:4445'.format(self.username, self.access_key)
        cmd_executor = 'http://{}/wd/hub'.format(hub_url)
        browser_profile = None
        if self.browser == 'firefox':
            browser_profile = f_profile
        elif self.browser == 'chrome':
            caps['disable-user-media-security'] = True
        # Try to start the remote webdriver a few times... For some reason
        # it fails sometimes with a ValueError.
        number_of_attempts = 10
        for attempt in range(number_of_attempts):
            try:
                self.drv = webdriver.Remote(
                    desired_capabilities=caps,
                    command_executor=cmd_executor,
                    browser_profile=browser_profile,
                )
                break
            except urllib.error.URLError:
                self.fail(
                    'Sauce Connect failure. Did you start Sauce Connect?'
                )
            except ValueError:
                if attempt == number_of_attempts - 1:
                    raise
                continue
        self.drv.implicitly_wait(10)

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

    def wait_for_element(self, identifier, by=By.ID, timeout=5, visible=False):
        visibility = EC.visibility_of_element_located
        presence = EC.presence_of_element_located
        loader = visibility if visible else presence
        load = loader((by, identifier))
        WebDriverWait(self.drv, timeout).until(load)

    def set_geolocation(self, lat=40, lng=-70):
        time.sleep(1)
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
        time.sleep(1)

    def click(self, element):
        element.click()
        time.sleep(1)

    def toggle_online(self):
        self.online = not self.online
        self.drv.execute_script(
            "navigator.__defineGetter__('onLine', function()"
            " {{return {}}});".format(str(self.online).lower())
        )


class TestAuth(DriverTest):
    @unittest.skipIf(
        os.environ.get('TRAVIS', False),
        'This test just refuses to work on Travis.'
    )
    def test_login(self):
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
        time.sleep(1)
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

        time.sleep(1)

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
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('2015/08/11')
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
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('3:33 PM')
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
        (
            self.drv
            .find_element_by_tag_name('input')
            .send_keys('2015/08/11 3:33 PM')
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
        time.sleep(1)
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

        self.toggle_online()  # TODO: have a js listener for this
        # so that the next two lines can go away
        self.click(self.drv.find_element_by_class_name('navigate-right'))
        self.click(self.drv.find_element_by_class_name('page_nav__prev'))

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

        self.drv.get('')  # unload the page
        self.get(enumerate_url)

        self.click(self.drv.find_elements_by_tag_name('button')[0])

        new_submission = self.get_last_submission(survey_id)

        self.assertIsNot(existing_submission, new_submission)
        self.assertEqual(new_submission.answers[0].answer, 3)
