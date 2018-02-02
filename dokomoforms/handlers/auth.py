"""Authentication handlers."""

from collections import OrderedDict
from datetime import datetime, timedelta
import uuid

from sqlalchemy.orm.exc import NoResultFound

import tornado.concurrent
import tornado.web
import tornado.gen
import tornado.httpclient

from passlib.hash import bcrypt_sha256

from dokomoforms.handlers.portier import get_verified_email
from dokomoforms.handlers.util import BaseHandler, authenticated_admin
from dokomoforms.models import User, Email


class VerifyLoginHandler(BaseHandler):

    """Handlers for portier verification."""

    def check_xsrf_cookie(self):

        """Disable XSRF check.
        OpenID doesn't reply with _xsrf header.
        https://github.com/portier/demo-rp/issues/10
        """
        pass

    async def post(self):

        """Verify the response from the portier broker."""

        if 'error' in self.request.arguments:
            raise tornado.web.HTTPError(400)
        token = self.get_argument('id_token')
        email = await get_verified_email(token)

        try:
            user = (
                self.session
                .query(User.id, User.name)
                .join(Email)
                .filter(Email.address == email)
                .one()
            )
        except NoResultFound:
            raise tornado.web.HTTPError(400)
        self.set_secure_cookie(
            'user', str(user.id),
            httponly=True, secure=True)
        self.redirect(self.get_argument('next', '/'))


class Logout(BaseHandler):

    """POST here to log out."""

    def post(self):
        """Delete the "user" cookie.

        Note that this can't be done in JavaScript because the user cookie is
        httponly.
        """
        self.clear_cookie('user')
        self.redirect('/')


class GenerateToken(BaseHandler):  # We should probably do this in JS

    """GET your token here. GETting twice resets the token."""

    @authenticated_admin
    def get(self):
        """Set a new token for the logged in user and return the token."""
        token = uuid.uuid4().hex
        user = self.current_user_model
        with self.session.begin():
            user.token = bcrypt_sha256.encrypt(token).encode()
            user.token_expiration = datetime.now() + timedelta(days=60)
        self.write(OrderedDict((
            ('token', token),
            ('expires_on', user.token_expiration.isoformat()),
        )))


class CheckLoginStatus(BaseHandler):

    """An endpoint for the application to check login status."""

    @tornado.web.authenticated
    def post(self):
        """2xx good, 5xx bad."""
        self.finish()
