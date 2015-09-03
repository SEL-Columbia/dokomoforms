"""Useful reusable functions for handlers, plus the BaseHandler."""
import tornado.web
from tornado.escape import to_unicode, json_decode

from dokomoforms.models import User, Survey


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

    def set_default_headers(self):
        """Add some security-flavored headers.

        https://news.ycombinator.com/item?id=10143082
        """
        super().set_default_headers()
        self.clear_header('Server')
        self.set_header('X-Frame-Options', 'DENY')
        self.set_header('X-Xss-Protection', '1; mode=block')
        self.set_header('X-Content-Type-Options', 'nosniff')
        self.set_header(
            'Content-Security-Policy',
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'"
            " cdn.leafletjs.com code.highcharts.com"
            " momentjs.com cdn.datatables.net login.persona.org; "
            "frame-src login.persona.org; "
            "style-src 'self' 'unsafe-inline'"
            " fonts.googleapis.com cdn.leafletjs.com;"
            "font-src 'self' fonts.googleapis.com fonts.gstatic.com;"
            "default-src 'self';"
        )

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

    def _get_current_user_id(self):
        """Get the current user's id for the templates.

        :return: a string contain the currently logged in user's uuid
        """
        if not self.current_user:
            return None
        return self.current_user_model.id

    def get_template_namespace(self):
        """Template functions.

        TODO: Find a way to get rid of this.
        @jmwohl
        """
        namespace = super().get_template_namespace()
        namespace.update({
            'surveys_for_menu': self._get_surveys_for_menu(),
            'current_user_id': self._get_current_user_id()
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
