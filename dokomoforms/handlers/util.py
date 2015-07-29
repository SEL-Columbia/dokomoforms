"""Useful reusable functions for handlers, plus the BaseHandler."""
import dateutil.parser

import tornado.web
from tornado.escape import to_unicode, json_decode

from dokomoforms.models import User, Survey


def iso_date_str_to_fmt_str(date, format_str):
    """Transform an ISO 8601 string.

    TODO: Remove the need for this.
    @jmwohl
    """
    if date is not None:
        return dateutil.parser.parse(date).strftime(format_str)
    else:
        return None


class BaseHandler(tornado.web.RequestHandler):

    """The base class for handlers.

    Makes the database session and current user available.
    """

    @property
    def session(self):
        """The SQLAlchemy session for interacting with the models.

        :return: the SQLAlchemy session
        """
        return self.application.session

    @property
    def current_user_model(self):
        """Return the current logged in User, or None."""
        current_user = self._current_user_cookie()
        if current_user:
            user_id = json_decode(current_user)['user_id']
            return self.session.query(User).get(user_id)
        return None

    def prepare(self):
        """Default behavior before any HTTP method.

        By default, just sets up the XSRF token.

        """
        # Just accessing the token makes the handler send it to the browser
        self.xsrf_token

    def get(self, *args, **kwargs):
        """404 unless this method is overridden.

        The presence of this GET method means that endpoints which only
        accept POST are hidden from browsers.

        :raise tornado.web.HTTPError: 404 Not Found
        """
        raise tornado.web.HTTPError(404)

    def _current_user_cookie(self) -> str:
        return self.get_secure_cookie('user')

    def get_current_user(self) -> str:
        """Make current_user accessible.

        You probably shouldn't override this method. It makes
        {{ current_user }} accessible to templates and self.current_user
        accessible to handlers.

        :return: a string containing the user name.
        """
        current_user = self._current_user_cookie()
        if current_user:
            return to_unicode(json_decode(current_user)['user_name'])
        return None

    def _get_surveys_for_menu(self):
        """The menu bar needs access to surveys.

        TODO: Get rid of this
        @jmwohl
        """
        if not self.current_user:
            return None
        return (
            self.session
            .query(Survey)
            .filter_by(creator_id=self.current_user_model.id)
            .order_by(Survey.created_on.desc())
            .limit(10)
        )

    def get_template_namespace(self):
        """Template functions.

        TODO: Find a way to get rid of this.
        @jmwohl
        """
        namespace = super().get_template_namespace()
        namespace.update({
            'iso_date_str_to_fmt_str': iso_date_str_to_fmt_str,
            'surveys_for_menu': self._get_surveys_for_menu(),
        })
        return namespace

    # def write_error(self, status_code, **kwargs):
    #     if status_code == 422 and 'exc_info' in kwargs:
    #         assert False, kwargs['exc_info'][0].args
    #         self.write(kwargs)
    #     else:
    #         super().write_error(status_code, **kwargs)


class BaseAPIHandler(BaseHandler):

    """The Tornado handler class for API resource classes."""

    @property
    def api_version(self):
        """The API version."""
        return self.application._api_version

    @property
    def api_root_path(self):
        """The API URL up to the version number."""
        return self.application._api_root_path

    def check_xsrf_cookie(self):
        """Do not check XSRF for an API request (usually)."""
        return None
