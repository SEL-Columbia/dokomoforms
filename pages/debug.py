"""Pages pertaining to debug-specific functionality."""

from db.auth_user import get_auth_user_by_email, UserDoesNotExistError
from pages.util.base import BaseHandler


class DebugLoginHandler(BaseHandler):
    """Use this page to log in as any user."""

    def get(self, email=""):
        try:
            get_auth_user_by_email(email)
            self.set_secure_cookie('user', email, expires_days=None,
                                   # secure=True,
                                   httponly=True,
            )
            self.write('You are now logged in as {}'.format(email))
        except UserDoesNotExistError:
            self.write('No such user')


class DebugLogoutHandler(BaseHandler):
    """Log out by visiting this page."""

    def get(self):
        self.clear_cookie('user')
        self.write('You have logged out.')
