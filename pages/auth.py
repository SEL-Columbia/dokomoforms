"""Pages pertaining to logging in and out."""

import urllib.parse

import tornado.web
import tornado.gen
import tornado.httpclient

import api.user
from pages.util.base import BaseHandler


class LoginHandler(BaseHandler):
    """POST here to create an account or log in using Mozilla Persona."""

    # TODO: Someone please help me write a test for this.

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        """
        This method POSTs to https://verifier.login.persona.org/verify to
        check the user's authentication. If it succeeds, it creates a new
        account if the e-mail is not in the DB and logs the user in.

        :raise tornado.web.HTTPError: if the Persona verified rejects the login
        """
        assertion = self.get_argument('assertion')
        http_client = tornado.httpclient.AsyncHTTPClient()
        url = 'https://verifier.login.persona.org/verify'
        input_data = {'assertion': assertion, 'audience': self.request.host}
        response = yield tornado.gen.Task(
            http_client.fetch,
            url,
            method='POST',
            body=urllib.parse.urlencode(input_data),
        )
        data = tornado.escape.json_decode(response.body)
        if data['status'] != "okay":
            raise tornado.web.HTTPError(400, "Failed assertion test")
        api.user.create_user(self.db, {'email': data['email']})
        self.set_secure_cookie('user', data['email'], expires_days=None,
                               # secure=True,
                               httponly=True)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        response = {'next_url': '/', 'email': data['email']}
        self.write(tornado.escape.json_encode(response))
        self.finish()


class LogoutHandler(BaseHandler):
    def post(self):
        self.clear_cookie('user')  # Move to js if possible
