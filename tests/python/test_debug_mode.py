"""Debug mode tests."""
import lzstring

from tornado.escape import json_decode, json_encode

from tests.python.util import (
    DokoHTTPTest, setUpModule, tearDownModule
)
utils = (setUpModule, tearDownModule)


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
