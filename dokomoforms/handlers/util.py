"""Useful reusable functions for handlers, plus the BaseHandler."""

import tornado.web
from tornado.escape import to_unicode


class BaseHandler(tornado.web.RequestHandler):
    """
    The base class for handlers. Makes the database session and current user
    available.
    """

    @property
    def session(self):
        """
        The SQLAlchemy session for interacting with the models.

        :return: the SQLAlchemy session
        """
        return self.application.session

    def prepare(self):
        """
        Default behavior before any HTTP method. By default, just sets up
        the XSRF token.

        """
        # Just accessing the token make the handler send it to the browser
        self.xsrf_token

    def get(self, *args, **kwargs):
        """
        The presence of this GET method means that endpoints which only
        accept POST are hidden from browsers.

        :raise tornado.web.HTTPError: 404 Not Found
        """
        raise tornado.web.HTTPError(404)

    def get_current_user(self) -> str:
        """
        You probably shouldn't override this method. It makes
        {{ current_user }} accessible to templates and self.current_user
        accessible to handlers.

        :return: a string containing the dictionary
                 {
                     'user_id': <UUID>,
                     'user_name': <name>
                 }
        """
        user = self.get_secure_cookie('user')
        return to_unicode(user) if user else None

    # def write_error(self, status_code, **kwargs):
    #     if status_code == 422 and 'exc_info' in kwargs:
    #         assert False, kwargs['exc_info'][0].args
    #         self.write(kwargs)
    #     else:
    #         super().write_error(status_code, **kwargs)
