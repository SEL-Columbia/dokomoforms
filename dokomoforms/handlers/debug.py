"""Pages pertaining to debug-specific functionality."""

from tornado.escape import json_encode
import tornado.web

from sqlalchemy.orm.exc import NoResultFound

from dokomoforms.models import User, SurveyCreator, Email
from dokomoforms.handlers.util import BaseHandler
from dokomoforms.options import options


class DebugUserCreationHandler(BaseHandler):
    """User this page to create a user."""

    def get(self, email=''):
        with self.session.begin():
            creator = SurveyCreator(
                name='debug_user',
                emails=[Email(address=email)],
            )
            self.session.add(creator)

        self.write('Created user {}'.format(email))
        self.set_status(201)


class DebugLoginHandler(BaseHandler):
    """Use this page to log in as any user."""

    def get(self, email=""):
        try:
            user = (
                self.session.query(User.id, User.name)
                .join(Email)
                .filter(Email.address == email)
                .one()
            )
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
            self.write({'email': email})
            self.finish()
        except NoResultFound:
            _ = self.locale.translate
            raise tornado.web.HTTPError(
                422,
                reason=_(
                    'There is no account associated with the e-mail'
                    ' address {}'.format(email)
                ),
            )


class DebugLogoutHandler(BaseHandler):
    """Log out by visiting this page."""

    def get(self):
        self.clear_cookie('user')
        self.write('You have logged out.')
