"""Base handler classes and utility functions."""
import functools
from pprint import pformat

from sqlalchemy.exc import IntegrityError
from tornado.escape import to_unicode, json_decode, json_encode
import tornado.web

from db.auth_user import verify_api_token
from utils.logger import setup_custom_logger


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
        user = self.get_secure_cookie('user')
        if user:
            return to_unicode(user)


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
    return header if header is not None else self.current_user


def get_json_request_body(self: tornado.web.RequestHandler) -> dict:
    """
    Get a JSON dict from a request body
    :param self: the Handler
    :return: the body as a JSON dict
    :raise tornado.web.HTTPError: 400 if the body cannot be parsed as JSON
    """
    try:
        return json_decode(to_unicode(self.request.body))
    except ValueError:
        raise tornado.web.HTTPError(400, reason=json_encode(
            {'message': 'Problems parsing JSON'}))


def validation_message(resource: str, field: str, code:str) -> str:
    """
    Create a standard error message.

    :param resource: the resource with which the method tried to interact
    :param field: the name of the field involved in the error
    :param code: the error
    :return: the error message
    """
    return json_encode({"message": "Validation Failed",
                        "errors": [{'resource': resource,
                                    'field': field,
                                    'code': code}]})


def catch_bare_integrity_error(method, logger=setup_custom_logger('dokomo')):
    """
    If an IntegrityError falls through a function, log it and raise the
    appropriate web error.

    :param method: the HTTP method
    :param logger: the logger to use (useful for testing)
    :return: the wrapped method
    :raise tornado.web.HTTPError: 422 when catching an IntegrityError
    """

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except IntegrityError as e:
            logger.error('\n' + pformat(e))
            reason = validation_message('submission', '', 'invalid')
            raise tornado.web.HTTPError(422, reason=reason)

    return wrapper
