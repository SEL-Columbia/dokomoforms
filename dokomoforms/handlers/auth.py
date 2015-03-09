"""Pages pertaining to logging in and out."""

import urllib.parse

from tornado.escape import json_decode, json_encode

import tornado.web
import tornado.gen
import tornado.httpclient

import dokomoforms.api.user as user_api
from dokomoforms.handlers.util.base import BaseHandler


class LoginHandler(BaseHandler):
    """POST here to create an account or log in using Mozilla Persona."""

    def _async_post(self, http_client, url, input_data):
        """
        POST asynchronously to a URL.

        :param http_client: the HTTP client to use
        :param url: the URL of the verifier service
        :param input_data: the assertion data dict
        :return: a Tornado Task
        """
        return tornado.gen.Task(
            http_client.fetch,
            url,
            method='POST',
            body=urllib.parse.urlencode(input_data),
        )

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        """
        This method uses Mozilla Persona to check if the user is
        authenticated. On success, it creates a new account if the e-mail is
        not in the DB and logs the user in.

        :raise tornado.web.HTTPError: if the Persona verifier rejects the login
        """
        assertion = self.get_argument('assertion')
        http_client = tornado.httpclient.AsyncHTTPClient()
        url = 'https://verifier.login.persona.org/verify'
        input_data = {'assertion': assertion, 'audience': self.request.host}
        response = yield self._async_post(http_client, url, input_data)
        data = json_decode(response.body)
        if data['status'] != 'okay':
            raise tornado.web.HTTPError(400, 'Failed assertion test')
        user_api.create_user(self.db, {'email': data['email']})
        self.set_secure_cookie('user', data['email'], expires_days=None,
                               # secure=True,
                               httponly=True)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        result = {'next_url': '/', 'email': data['email']}
        self.write(json_encode(result))
        self.finish()


class LogoutHandler(BaseHandler):
    def post(self):
        self.clear_cookie('user')  # Move to js if possible
