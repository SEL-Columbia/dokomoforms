"""Handler tests"""
from unittest.mock import patch

from bs4 import BeautifulSoup

from tornado.escape import json_decode, json_encode
import tornado.gen
import tornado.httpclient
import tornado.testing

from tests.util import DokoHTTPTest, setUpModule, tearDownModule

utils = (setUpModule, tearDownModule)

import dokomoforms.handlers as handlers
import dokomoforms.handlers.auth


class TestIndex(DokoHTTPTest):
    def test_get_not_logged_in(self):
        response = self.fetch('/', method='GET', _logged_in_user=None)
        response_soup = BeautifulSoup(response.body, 'html.parser')
        links = response_soup.select('a.btn-login.btn-large')
        self.assertEqual(len(links), 1, msg=response.body)

    def test_get_logged_in(self):
        response = self.fetch('/', method='GET')
        response_soup = BeautifulSoup(response.body, 'html.parser')
        links = response_soup.select('a.btn-login.btn-large')
        self.assertEqual(len(links), 0, msg=response.body)
        self.assertIn(
            'Account Overview', response.body.decode(), msg=response.body
        )


class TestAuth(DokoHTTPTest):
    @tornado.testing.gen_test
    def test_async_post(self):
        con_dummy = lambda: None
        con_dummy.set_close_callback = lambda x: None
        dummy = lambda: None
        dummy.connection = con_dummy
        login = handlers.Login(self.app, dummy)
        with patch.object(handlers.Logout, 'check_xsrf_cookie') as p:
            p.return_value = None
            response = yield login._async_post(
                tornado.httpclient.AsyncHTTPClient(),
                self.get_url('/user/logout'),
                '',
            )
        self.assertEqual(response.code, 200, msg=response.body)

    def test_login_success(self):
        with patch.object(handlers.Login, '_async_post') as p:
            dummy = lambda: None
            dummy.body = json_encode(
                {'status': 'okay', 'email': 'test_creator@fixtures.com'}
            )
            p.return_value = tornado.gen.Task(
                lambda callback=None: callback(dummy)
            )
            response = self.fetch(
                '/user/login?assertion=woah', method='POST', body='',
                _logged_in_user=None
            )
        self.assertEqual(response.code, 200, msg=response.body)
        self.assertNotIn('secure', response.headers['Set-Cookie'].lower())

    def test_login_success_secure_cookie(self):
        dokomoforms.handlers.auth.options.https = True
        with patch.object(handlers.Login, '_async_post') as p:
            dummy = lambda: None
            dummy.body = json_encode(
                {'status': 'okay', 'email': 'test_creator@fixtures.com'}
            )
            p.return_value = tornado.gen.Task(
                lambda callback=None: callback(dummy)
            )
            response = self.fetch(
                '/user/login?assertion=woah', method='POST', body='',
                _logged_in_user=None
            )
        self.assertEqual(response.code, 200, msg=response.body)
        self.assertIn('secure', response.headers['Set-Cookie'].lower())

    def test_login_email_does_not_exist(self):
        with patch.object(handlers.Login, '_async_post') as p:
            dummy = lambda: None
            dummy.body = json_encode({'status': 'okay', 'email': 'test_email'})
            p.return_value = tornado.gen.Task(
                lambda callback=None: callback(dummy)
            )
            response = self.fetch(
                '/user/login?assertion=woah', method='POST', body='',
                _logged_in_user=None
            )
        self.assertEqual(response.code, 422, msg=response.body)

    def test_login_fail(self):
        with patch.object(handlers.Login, '_async_post') as p:
            dummy = lambda: None
            dummy.body = json_encode(
                {'status': 'not okay', 'email': 'test_creator@fixtures.com'}
            )
            p.return_value = tornado.gen.Task(
                lambda callback=None: callback(dummy)
            )
            response = self.fetch(
                '/user/login?assertion=woah', method='POST', body='',
                _logged_in_user=None
            )
        self.assertEqual(response.code, 400, msg=response.body)


class TestEnumerate(DokoHTTPTest):
    def test_get_public_survey_not_logged_in(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        url = '/enumerate/' + survey_id
        response = self.fetch(url, method='GET', _logged_in_user=None)
        response_soup = BeautifulSoup(response.body, 'html.parser')
        scripts = response_soup.findAll('script')
        self.assertGreater(len(scripts), 0, msg=response.body)
        survey = response_soup.findAll('script')[-1].text[6:-3]
        try:
            survey = json_decode(survey)
        except ValueError:
            self.fail(response)
        api_url = self.api_root + '/surveys/' + survey_id
        self.assertEqual(
            survey,
            json_decode(
                self.fetch(api_url, method='GET', _logged_in_user=None).body
            )
        )

    def test_get_public_survey_logged_in(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        url = '/enumerate/' + survey_id
        response = self.fetch(url, method='GET')
        response_soup = BeautifulSoup(response.body, 'html.parser')
        scripts = response_soup.findAll('script')
        self.assertGreater(len(scripts), 0, msg=response.body)
        survey = response_soup.findAll('script')[-1].text[6:-3]
        try:
            survey = json_decode(survey)
        except ValueError:
            self.fail(response)
        api_url = self.api_root + '/surveys/' + survey_id
        self.assertEqual(
            survey,
            json_decode(
                self.fetch(api_url, method='GET').body
            )
        )

    def test_get_enumerator_only_survey_not_logged_in(self):
        survey_id = 'c0816b52-204f-41d4-aaf0-ac6ae2970925'
        url = '/enumerate/' + survey_id
        response = self.fetch(
            url, method='GET', follow_redirects=False, _logged_in_user=None
        )
        self.assertEqual(response.code, 302)

    def test_get_enumerator_only_survey_logged_in(self):
        survey_id = 'c0816b52-204f-41d4-aaf0-ac6ae2970925'
        url = '/enumerate/' + survey_id
        response = self.fetch(url, method='GET')
        response_soup = BeautifulSoup(response.body, 'html.parser')
        scripts = response_soup.findAll('script')
        self.assertGreater(len(scripts), 0, msg=response.body)
        survey = response_soup.findAll('script')[-1].text[6:-3]
        try:
            survey = json_decode(survey)
        except ValueError:
            self.fail(response)
        api_url = self.api_root + '/surveys/' + survey_id
        self.assertEqual(
            survey,
            json_decode(
                self.fetch(api_url, method='GET').body
            )
        )
