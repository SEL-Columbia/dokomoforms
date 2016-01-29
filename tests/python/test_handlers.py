"""Handler tests"""
from types import SimpleNamespace
from unittest.mock import patch
import uuid

from bs4 import BeautifulSoup

import lzstring

import sqlalchemy as sa
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.sql.functions import count
from sqlalchemy.dialects import postgresql as pg

from tornado.escape import json_decode, json_encode, url_escape
import tornado.gen
import tornado.httpclient
import tornado.testing
import tornado.web

from tests.python.util import (
    DokoHTTPTest, setUpModule, tearDownModule
)

utils = (setUpModule, tearDownModule)

import dokomoforms.handlers as handlers
import dokomoforms.handlers.auth
from dokomoforms.handlers.util import (
    BaseHandler, BaseAPIHandler, authenticated_admin
)
import dokomoforms.models as models


class TestUtil(DokoHTTPTest):
    def test_authenticated_admin_not_logged_in_bad_method(self):
        """You should get a 403."""
        method = authenticated_admin(lambda x: x)
        args = SimpleNamespace(
            current_user=None,
            request=SimpleNamespace(method='POST'),
        )
        self.assertRaises(tornado.web.HTTPError, method, args)
        try:
            method(args)
        except tornado.web.HTTPError as err:
            status = err.status_code
        self.assertEqual(status, 403)

    def test_authenticated_admin_not_logged_in_ok_method(self):
        """You should get a redirect to the login page."""
        class Redirect(Exception):
            """For testing purposes"""
        def redirect(url):
            raise Redirect(url)

        method = authenticated_admin(lambda x: x)
        args = SimpleNamespace(
            current_user=None,
            request=SimpleNamespace(
                method='GET',
                uri='/admin',
            ),
            get_login_url=lambda: '/',
            redirect=redirect,
        )
        self.assertRaises(Redirect, method, args)
        try:
            method(args)
        except Redirect as redirect:
            url = redirect.args[0]
        self.assertEqual(url, '/?next=%2Fadmin')

    def test_authenticated_admin_enumerator_logged_in(self):
        """You should get a 403."""
        method = authenticated_admin(lambda x: x)
        args = SimpleNamespace(
            current_user=object(),
            current_user_model=(
                self.session
                .query(models.User)
                .get('a7becd02-1a3f-4c1d-a0e1-286ba121aef3')
            ),
        )
        self.assertRaises(tornado.web.HTTPError, method, args)
        try:
            method(args)
        except tornado.web.HTTPError as err:
            status = err.status_code
        self.assertEqual(status, 403)

    def test_authenticated_admin_administrator_logged_in(self):
        """The method should be evaluated."""
        method = authenticated_admin(lambda x: x)
        args = SimpleNamespace(
            current_user=object(),
            current_user_model=(
                self.session
                .query(models.User)
                .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
            ),
        )
        result = method(args)
        self.assertIs(result, args)


class TestIndex(DokoHTTPTest):
    def test_get_not_logged_in(self):
        response = self.fetch('/', method='GET', _logged_in_user=None)
        response_soup = BeautifulSoup(response.body, 'html.parser')
        links = response_soup.select('a.btn-login.btn-large')
        self.assertEqual(len(links), 1, msg=response.body)

    def test_get_logged_in_admin(self):
        num_surveys = (
            self.session
            .query(count(models.Survey.id))
            .filter_by(creator_id='b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
            .scalar()
        )
        response = self.fetch('/', method='GET')
        response_soup = BeautifulSoup(response.body, 'html.parser')
        links = response_soup.select('a.btn-login.btn-large')
        self.assertEqual(len(links), 0, msg=response.body)
        self.assertIn(
            'Account Overview', response.body.decode(), msg=response.body
        )
        survey_dropdown = (
            response_soup.find('ul', {'aria-labelledby': 'SurveysDropdown'})
        )
        self.assertEqual(
            len(survey_dropdown.findAll('li')),
            min(num_surveys, BaseHandler.num_surveys_for_menu),
            msg=survey_dropdown
        )

    def test_get_logged_in_enumerator(self):
        response = self.fetch(
            '/',
            method='GET',
            _logged_in_user='a7becd02-1a3f-4c1d-a0e1-286ba121aef3'
        )
        self.assertTrue(response.effective_url.endswith('/enumerate'))


class TestNotFound(DokoHTTPTest):
    def test_bogus_url(self):
        response = self.fetch('/🍤')
        self.assertEqual(response.code, 404, msg=response)

    def test_bogus_GET(self):
        response = self.fetch(
            '/user/login', method='GET', _logged_in_user=None
        )
        self.assertEqual(response.code, 404, msg=response)

    def test_bogus_survey_id(self):
        fake_id = str(uuid.uuid4())
        response = self.fetch('/enumerate/{}'.format(fake_id))
        self.assertEqual(response.code, 404, msg=response)


class TestDebug(DokoHTTPTest):
    def tearDown(self):
        try:
            self.fetch('/debug/toggle_facilities?state=true')
        finally:
            super().tearDown()

    def test_debug_create(self):
        response = self.fetch(
            '/debug/create/a@a', method='GET', _logged_in_user=None
        )
        self.assertEqual(response.code, 201, msg=response)

    def test_debug_create_email_exists(self):
        response = self.fetch(
            '/debug/create/test_creator@fixtures.com', method='GET',
            _logged_in_user=None
        )
        self.assertEqual(response.code, 200, msg=response)

    def test_login_email_does_not_exist(self):
        response = self.fetch(
            '/debug/login/a@a', method='GET', _logged_in_user=None
        )
        self.assertEqual(response.code, 422, msg=response)

    def test_logout(self):
        response = self.fetch(
            '/debug/logout', method='GET', _logged_in_user=None
        )
        self.assertEqual(response.code, 200, msg=response)

    def test_persona_verifier(self):
        response = self.fetch(
            '/debug/persona_verify', method='POST', body='',
            _logged_in_user=None, _disable_xsrf=False,
        )
        self.assertEqual(response.code, 200, msg=response)

    def test_debug_revisit(self):
        response = self.fetch(
            '/debug/facilities', method='GET',
            _logged_in_user=None, _disable_xsrf=False,
        )
        self.assertEqual(response.code, 200, msg=response)

    def test_debug_post_revisit(self):
        body = {
            'uuid': 'a',
            'name': 'b',
            'properties': {},
            'coordinates': [0, 0],
        }
        response = self.fetch(
            '/debug/facilities', method='POST', body=json_encode(body),
            _disable_xsrf=False
        )
        self.assertEqual(response.code, 201, msg=response.body)

        facility_response = self.fetch('/debug/facilities')
        lzs = lzstring.LZString()
        facility_json = json_decode(facility_response.body)
        compressed = facility_json['facilities']['children']['wn']['data'][0]
        facilities = lzs.decompressFromUTF16(compressed)
        self.assertEqual(json_decode(facilities)[-1]['name'], 'b')

    def test_debug_toggle_revisit(self):
        response = self.fetch(
            '/debug/toggle_facilities?state=false', method='GET',
            _logged_in_user=None, _disable_xsrf=False,
        )
        self.assertEqual(response.code, 200, msg=response)

        revisit_response = self.fetch(
            '/debug/facilities', method='GET',
            _logged_in_user=None, _disable_xsrf=False,
        )
        self.assertEqual(revisit_response.code, 502, msg=response)

        revisit_response = self.fetch(
            '/debug/facilities', method='POST', body='{}',
            _logged_in_user=None, _disable_xsrf=False,
        )
        self.assertEqual(revisit_response.code, 502, msg=response)

        toggle_response = self.fetch(
            '/debug/toggle_facilities', method='GET',
            _logged_in_user=None, _disable_xsrf=False,
        )
        self.assertEqual(toggle_response.code, 200, msg=response)

        revisit_again_response = self.fetch(
            '/debug/facilities', method='GET',
            _logged_in_user=None, _disable_xsrf=False,
        )
        self.assertEqual(revisit_again_response.code, 200, msg=response)

    def test_debug_toggle_revisit_with_argument(self):
        response = self.fetch(
            '/debug/toggle_facilities', method='GET',
            _logged_in_user=None, _disable_xsrf=False,
        )
        self.assertEqual(response.code, 200, msg=response)

        revisit_response = self.fetch(
            '/debug/facilities', method='GET',
            _logged_in_user=None, _disable_xsrf=False,
        )
        self.assertEqual(revisit_response.code, 502, msg=response)

        toggle_response = self.fetch(
            '/debug/toggle_facilities?state=true', method='GET',
            _logged_in_user=None, _disable_xsrf=False,
        )
        self.assertEqual(toggle_response.code, 200, msg=response)

        revisit_again_response = self.fetch(
            '/debug/facilities', method='GET',
            _logged_in_user=None, _disable_xsrf=False,
        )
        self.assertEqual(revisit_again_response.code, 200, msg=response)


class TestHeaders(DokoHTTPTest):
    def test_secure_headers(self):
        response = self.fetch('/', method='GET', _logged_in_user=None)
        self.assertNotIn(
            'server',
            {header.lower() for header in response.headers}
        )
        self.assertIn('X-Frame-Options', response.headers)
        self.assertIn('X-Xss-Protection', response.headers)
        self.assertIn('X-Content-Type-Options', response.headers)
        self.assertIn('Content-Security-Policy', response.headers)


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
        dokomoforms.handlers.auth.options.https = False
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
        self.assertEqual(
            response.headers['Set-Cookie'].lower().count('secure'),
            1
        )

    def test_login_as_admin_first_time(self):
        admin_emails = (
            self.session
            .query(models.Email)
            .filter_by(address='admin@email.com')
            .all()
        )
        self.assertEqual(len(admin_emails), 0)

        dokomoforms.handlers.auth.options.https = False
        dokomoforms.handlers.auth.options.admin_email = 'admin@email.com'
        with patch.object(handlers.Login, '_async_post') as p:
            dummy = lambda: None
            dummy.body = json_encode(
                {'status': 'okay', 'email': 'admin@email.com'}
            )
            p.return_value = tornado.gen.Task(
                lambda callback=None: callback(dummy)
            )
            response = self.fetch(
                '/user/login?assertion=woah', method='POST', body='',
                _logged_in_user=None
            )
        self.assertEqual(response.code, 200, msg=response.body)
        self.assertEqual(
            response.headers['Set-Cookie'].lower().count('secure'),
            1
        )

        new_admin_emails = (
            self.session
            .query(models.Email)
            .filter_by(address='admin@email.com')
            .all()
        )
        self.assertEqual(len(new_admin_emails), 1)

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

    def test_check_login_status_logged_out(self):
        response = self.fetch(
            '/user/authenticated',
            method='POST', _logged_in_user=None, body=''
        )
        self.assertEqual(response.code, 403)

    def test_check_login_status_logged_in(self):
        response = self.fetch(
            '/user/authenticated',
            method='POST', body=''
        )
        self.assertEqual(response.code, 200)


class TestBaseHandler(DokoHTTPTest):
    def test_user_default_language_not_logged_in(self):
        dummy_request = SimpleNamespace(
            cookies={'user': SimpleNamespace(
                value=str(uuid.uuid4())
            )},
            connection=SimpleNamespace(
                set_close_callback=lambda _: None,
            ),
        )
        handler = BaseHandler(self.app, dummy_request)
        self.assertIsNone(handler.user_default_language)
        self.assertIsNone(handler.current_user_model)

    def test_user_default_language_logged_in(self):
        dummy_request = SimpleNamespace(
            cookies={'user': SimpleNamespace(
                value='b7becd02-1a3f-4c1d-a0e1-286ba121aef4',
            )},
            connection=SimpleNamespace(
                set_close_callback=lambda _: None,
            ),
        )
        with patch.object(BaseHandler, '_current_user_cookie') as p:
            p.return_value = 'b7becd02-1a3f-4c1d-a0e1-286ba121aef4'
            handler = BaseHandler(self.app, dummy_request)
            self.assertEqual(handler.user_default_language, 'English')

    def test_user_survey_language_not_logged_in(self):
        dummy_request = SimpleNamespace(
            cookies={'user': SimpleNamespace(
                value=str(uuid.uuid4())
            )},
            connection=SimpleNamespace(
                set_close_callback=lambda _: None,
            ),
        )
        handler = BaseHandler(self.app, dummy_request)
        self.assertIsNone(handler.user_survey_language('any survey'))
        self.assertIsNone(handler.current_user_model)

    def test_clear_user_cookie_if_not_uuid(self):
        dummy_request = lambda: None
        cookie_object = lambda: None
        cookie_object.value = str(uuid.uuid4())
        dummy_request.cookies = {'user': cookie_object}
        dummy_connection = lambda: None
        dummy_close_callback = lambda _: None
        dummy_connection.set_close_callback = dummy_close_callback
        dummy_request.connection = dummy_connection
        with patch.object(BaseHandler, '_current_user_cookie') as p:
            p.return_value = 'not a UUID'
            handler = BaseHandler(self.app, dummy_request)
            self.assertEqual(handler.get_cookie('user'), cookie_object.value)
            self.assertIsNone(handler.current_user_model)

    def test_underscore_t_no_preference(self):
        dummy_request = SimpleNamespace(
            cookies={'user': SimpleNamespace(
                value=str(uuid.uuid4())
            )},
            connection=SimpleNamespace(
                set_close_callback=lambda _: None,
            ),
        )
        handler = BaseHandler(self.app, dummy_request)
        result = handler._t(
            {'English': 'text'},
            SimpleNamespace(default_language='English')
        )
        self.assertEqual(result, 'text')

    def test_underscore_t_no_preference_no_translation(self):
        """Is this the desired behavior? Maybe."""
        dummy_request = SimpleNamespace(
            cookies={'user': SimpleNamespace(
                value=str(uuid.uuid4())
            )},
            connection=SimpleNamespace(
                set_close_callback=lambda _: None,
            ),
        )
        handler = BaseHandler(self.app, dummy_request)
        self.assertRaises(
            KeyError,
            handler._t,
            {'English': 'text'},
            SimpleNamespace(default_language='French'),
        )

    def test_underscore_t_user_default(self):
        dummy_request = SimpleNamespace(
            cookies={'user': SimpleNamespace(
                value='b7becd02-1a3f-4c1d-a0e1-286ba121aef4'
            )},
            connection=SimpleNamespace(
                set_close_callback=lambda _: None,
            ),
        )
        with patch.object(BaseHandler, '_current_user_cookie') as p:
            p.return_value = 'b7becd02-1a3f-4c1d-a0e1-286ba121aef4'
            handler = BaseHandler(self.app, dummy_request)
            result = handler._t(
                {'English': 'text'},
                SimpleNamespace(id=None, default_language='French')
            )
            self.assertEqual(result, 'text')

    def test_underscore_t_user_survey_default(self):
        with self.session.begin():
            user = (
                self.session
                .query(models.User)
                .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
            )
            user.preferences['woah survey_id'] = {
                'display_language': 'Cool language'
            }
            flag_modified(user, 'preferences')
            self.session.add(user)

        dummy_request = SimpleNamespace(
            cookies={'user': SimpleNamespace(
                value='b7becd02-1a3f-4c1d-a0e1-286ba121aef4'
            )},
            connection=SimpleNamespace(
                set_close_callback=lambda _: None,
            ),
        )
        with patch.object(BaseHandler, '_current_user_cookie') as p:
            p.return_value = 'b7becd02-1a3f-4c1d-a0e1-286ba121aef4'
            handler = BaseHandler(self.app, dummy_request)
            result = handler._t(
                {'Cool language': 'text'},
                SimpleNamespace(id='woah survey_id', default_language='French')
            )
            self.assertEqual(result, 'text')


class TestBaseAPIHandler(DokoHTTPTest):
    def test_api_version(self):
        dummy_request = lambda: None
        dummy_connection = lambda: None
        dummy_close_callback = lambda _: None
        dummy_connection.set_close_callback = dummy_close_callback
        dummy_request.connection = dummy_connection
        handler = BaseAPIHandler(self.app, dummy_request)
        self.assertEqual(handler.api_version, 'v0')

    def test_api_root_path(self):
        dummy_request = lambda: None
        dummy_connection = lambda: None
        dummy_close_callback = lambda _: None
        dummy_connection.set_close_callback = dummy_close_callback
        dummy_request.connection = dummy_connection
        handler = BaseAPIHandler(self.app, dummy_request)
        self.assertEqual(handler.api_root_path, '/api/v0')


class TestEnumerate(DokoHTTPTest):
    def survey_from_script(self, script):
        return script.text.rsplit(',', 1)[0][13:]

    def test_get_public_survey_not_logged_in(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        url = '/enumerate/' + survey_id
        response = self.fetch(url, method='GET', _logged_in_user=None)
        response_soup = BeautifulSoup(response.body, 'html.parser')
        scripts = response_soup.findAll('script')
        self.assertGreater(len(scripts), 0, msg=response.body)
        # find the last script, right split on first comma, take the first
        # element from the 7th character onward
        survey = self.survey_from_script(response_soup.findAll('script')[-1])
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

    def test_get_public_survey_by_title_not_logged_in(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        with self.session.begin():
            survey = self.session.query(models.Survey).get(survey_id)
            survey.url_slug = 'url_slug'
        url = '/enumerate/url_slug'
        response = self.fetch(url, method='GET', _logged_in_user=None)
        body = response.body

        safe_url = '/enumerate/' + survey_id
        safe_response = self.fetch(safe_url, _logged_in_user=None)
        safe_body = safe_response.body

        self.assertEqual(body, safe_body)

    def test_get_public_survey_by_title_404(self):
        url = '/enumerate/aaa'
        response = self.fetch(url, method='GET', _logged_in_user=None)
        self.assertEqual(response.code, 404)

    def test_get_public_survey_logged_in(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        url = '/enumerate/' + survey_id
        response = self.fetch(url, method='GET')
        response_soup = BeautifulSoup(response.body, 'html.parser')
        scripts = response_soup.findAll('script')
        self.assertGreater(len(scripts), 0, msg=response.body)
        # find the last script, right split on first comma, take the first
        # element from the 7th character onward
        survey = self.survey_from_script(response_soup.findAll('script')[-1])
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
        self.assertEqual(
            response.headers['Location'], '/?next=' + url_escape(url)
        )

    def test_get_enumerator_only_survey_by_title_not_logged_in(self):
        survey_id = 'c0816b52-204f-41d4-aaf0-ac6ae2970925'
        with self.session.begin():
            survey = self.session.query(models.Survey).get(survey_id)
            survey.url_slug = 'url_slug'
        url = '/enumerate/url_slug'
        response = self.fetch(
            url, method='GET', follow_redirects=False, _logged_in_user=None
        )
        self.assertEqual(response.code, 302)
        self.assertEqual(
            response.headers['Location'], '/?next=' + url_escape(url)
        )

    def test_get_enumerator_only_survey_logged_in(self):
        survey_id = 'c0816b52-204f-41d4-aaf0-ac6ae2970925'
        url = '/enumerate/' + survey_id
        response = self.fetch(url, method='GET')
        response_soup = BeautifulSoup(response.body, 'html.parser')
        scripts = response_soup.findAll('script')
        self.assertGreater(len(scripts), 0, msg=response.body)
        # find the last script, right split on first comma, take the first
        # element from the 7th character onward
        survey = self.survey_from_script(response_soup.findAll('script')[-1])
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

    def test_get_enumerator_only_survey_by_title_logged_in(self):
        survey_id = 'c0816b52-204f-41d4-aaf0-ac6ae2970925'
        with self.session.begin():
            survey = self.session.query(models.Survey).get(survey_id)
            survey.url_slug = 'url_slug'
        url = '/enumerate/url_slug'
        response = self.fetch(url, method='GET')
        body = response.body

        safe_url = '/enumerate/' + survey_id
        safe_response = self.fetch(safe_url)
        safe_body = safe_response.body

        self.assertEqual(response.code, safe_response.code)
        self.assertEqual(body, safe_body)

    def test_get_enumerator_only_survey_logged_in_not_an_enumerator(self):
        with self.session.begin():
            some_user = models.User(name='some_user')
            self.session.add(some_user)

        survey_id = 'c0816b52-204f-41d4-aaf0-ac6ae2970925'
        url = '/enumerate/' + survey_id

        response = self.fetch(
            url,
            method='GET',
            follow_redirects=False,
            _logged_in_user=some_user.id,
        )

        self.assertEqual(response.code, 403)

    def test_get_enum_only_survey_by_title_logged_in_not_an_enumerator(self):
        with self.session.begin():
            some_user = models.User(name='some_user')
            self.session.add(some_user)

        survey_id = 'c0816b52-204f-41d4-aaf0-ac6ae2970925'
        with self.session.begin():
            survey = self.session.query(models.Survey).get(survey_id)
            survey.url_slug = 'url_slug'
        url = '/enumerate/url_slug'

        response = self.fetch(
            url,
            method='GET',
            follow_redirects=False,
            _logged_in_user=some_user.id,
        )

        self.assertEqual(response.code, 403)


class TestView(DokoHTTPTest):
    def test_view_survey(self):
        survey_id = 'c0816b52-204f-41d4-aaf0-ac6ae2970925'
        url = '/admin/' + survey_id
        response = self.fetch(url, method='GET').body.decode()

        self.assertIn('Survey Info', response)
        self.assertIn('Activity Graph', response)
        self.assertIn('Submissions', response)

    def test_view_data(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        url = '/admin/data/' + survey_id
        response = self.fetch(url, method='GET')
        response_soup = BeautifulSoup(response.body, 'html.parser')
        questions = response_soup.findAll('div', {'class': 'question-stats'})
        self.assertEqual(len(questions), 5)

    def test_view_data_with_map_location(self):
        survey_id = (
            self.session
            .query(models.SurveyNode.root_survey_id)
            .filter(
                sa.cast(
                    models.SurveyNode.type_constraint, pg.TEXT
                ) == 'location'
            )
            .scalar()
        )
        url = '/admin/data/' + survey_id
        response = self.fetch(url, method='GET')
        response_soup = BeautifulSoup(response.body, 'html.parser')
        questions = response_soup.findAll('div', {'class': 'question-stats'})
        self.assertEqual(len(questions), 1)

    def test_view_data_with_map_facility(self):
        survey_id = (
            self.session
            .query(models.SurveyNode.root_survey_id)
            .filter(
                sa.cast(
                    models.SurveyNode.type_constraint, pg.TEXT
                ) == 'facility'
            )
            .scalar()
        )
        url = '/admin/data/' + survey_id
        response = self.fetch(url, method='GET')
        response_soup = BeautifulSoup(response.body, 'html.parser')
        questions = response_soup.findAll('div', {'class': 'question-stats'})
        self.assertEqual(len(questions), 1)

    def test_view_submission(self):
        submission_id = (
            self.session.query(models.Submission.id).limit(1).scalar()
        )
        submission_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970924'
        url = '/admin/submission/' + submission_id
        response = self.fetch(url, method='GET').body.decode()
        self.assertIn('Submission Detail', response)

    def test_view_user_administration(self):
        url = '/admin/user-administration'
        response = self.fetch(url, method='GET').body.decode()
        self.assertIn('Users', response)
