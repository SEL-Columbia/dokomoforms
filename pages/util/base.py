"""Base handler classes and utility functions."""
from tornado.escape import to_unicode

import tornado.web

from db.auth_user import verify_api_token


class BaseHandler(tornado.web.RequestHandler):
    """Common handler functions here (e.g. user auth, template helpers)"""

    def prepare(self):
        """
        This method runs before the HTTP-handling methods. It sets the XSRF
        token cookie.

        """
        self.xsrf_token  # accessing this property sets the cookie on the page

    def get(self):
        """
        The default behavior is to raise a 404 (hiding the existence of the
        endpoint). Override this method to render something instead.

        :raise tornado.web.HTTPError: 404, always
        """
        raise tornado.web.HTTPError(404)

    def get_current_user(self) -> str:
        """
        See http://tornado.readthedocs.org/en/latest/guide/security.html
        #user-authentication

        :return: the current user's e-mail address
        """
        return self.get_secure_cookie('user')


class APIHandler(BaseHandler):
    """Handler for API endpoints."""

    def prepare(self):
        """
        Before an HTTP method runs, this checks that either the user is
        logged  in or a valid API token has been supplied.

        :raise tornado.web.HTTPError: 403, if neither condition is true
        """
        if not self.current_user:
            token = self.request.headers.get('Token', None)
            email = self.request.headers.get('Email', None)
            if (token is None) or (email is None):
                raise tornado.web.HTTPError(403)
            if not verify_api_token(token=token, email=email):
                raise tornado.web.HTTPError(403)


def get_email(self: APIHandler) -> str:
    """
    Get the user's e-mail address from the header given to the API endpoint
    or the currently logged-in user account.

    :param self: the API endpoint handler
    :return: the e-mail address
    """
    header = self.request.headers.get('Email', None)
    return header if header is not None else to_unicode(self.current_user)
