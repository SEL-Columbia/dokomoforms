"""Authentication handlers."""

import urllib.parse

from tornado.escape import json_decode, json_encode
import tornado.web
import tornado.gen
import tornado.httpclient

from sqlalchemy.orm.exc import NoResultFound

from dokomoforms.options import options
from dokomoforms.handlers.util import BaseHandler
from dokomoforms.models import User, Email


class Login(BaseHandler):
    def _async_post(self, http_client, url, input_data):
        return tornado.gen.Task(
            http_client.fetch,
            url,
            method='POST',
            body=urllib.parse.urlencode(input_data),
        )

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        assertion = self.get_argument('assertion')
        http_client = tornado.httpclient.AsyncHTTPClient()
        url = 'https://verifier.login.persona.org/verify'
        input_data = {'assertion': assertion, 'audience': self.request.host}
        response = yield self._async_post(http_client, url, input_data)
        data = json_decode(response.body)
        if data['status'] != 'okay':
            raise tornado.web.HTTPError(400, 'Failed assertion test')

        try:
            user = self.session.query(User.id, User.name).join(Email).filter(
                Email.address == data['email']
            ).one()
            cookie_options = {
                'expires_days': None,
                'httponly': True,
            }
            if options.https:
                cookie_options['secure'] = True
            self.set_secure_cookie(
                'user',
                json_encode({'user_id': user.id, 'user_name': user.name}),
                **cookie_options
            )
            self.write({'email': data['email']})
            self.finish()
        except NoResultFound:
            _ = self.locale.translate
            raise tornado.web.HTTPError(
                422,
                reason=_(
                    'There is no account associated with the e-mail'
                    ' address {}'.format(data['email'])
                ),
            )


class Logout(BaseHandler):
    def post(self):
        self.clear_cookie('user')
