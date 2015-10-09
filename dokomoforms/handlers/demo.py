"""Pages pertaining to demo mode functionality."""
import uuid

from tornado.escape import json_encode

from dokomoforms.models import Administrator, Email
from dokomoforms.handlers.util import BaseHandler


class DemoUserCreationHandler(BaseHandler):

    """Use this page to create a demo user."""

    def get(self):
        """Create a new demo account and log in."""
        new_id = uuid.uuid4()
        name = 'demo-{}'.format(new_id)
        email = '{}@dokomoforms.org'.format(name)
        with self.session.begin():
            user = Administrator(
                name=name,
                emails=[Email(address=email)],
            )
            self.session.add(user)
        cookie_options = {
            'expires_days': None,
            'httponly': True,
        }
        self.set_secure_cookie(
            'user',
            json_encode({'user_id': user.id, 'user_name': user.name}),
            **cookie_options
        )
        self.redirect('/')


class DemoLogoutHandler(BaseHandler):

    """Delete your demo account by visiting this page."""

    def get(self):
        """Clear the 'user' cookie and delete the user."""
        self.clear_cookie('user')
        if self.current_user_model:
            with self.session.begin():
                self.session.delete(self.current_user_model)
        self.redirect('/')
