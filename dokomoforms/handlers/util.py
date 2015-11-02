"""Useful reusable functions for handlers, plus the BaseHandler."""
from sqlalchemy.exc import StatementError
from sqlalchemy.orm.exc import NoResultFound

import tornado.web
from tornado.escape import to_unicode, json_encode

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
        current_user_id = self._current_user_cookie()
        if current_user_id:
            cuid = to_unicode(current_user_id)
            try:
                return self.session.query(User).get(cuid)
            except StatementError:
                self.clear_cookie('user')
        return None

    @property
    def user_default_language(self):
        """Return the logged-in User's default language, or None."""
        user = self.current_user_model
        if user:
            return user.preferences['default_language']
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
            " momentjs.com cdn.datatables.net https://login.persona.org; "
            "frame-src login.persona.org; "
            "style-src 'self' 'unsafe-inline'"
            " fonts.googleapis.com cdn.leafletjs.com *.cloudfront.net;"
            "font-src 'self' fonts.googleapis.com fonts.gstatic.com;"
            "img-src 'self' *.tile.openstreetmap.org data: blob:;"
            "object-src 'self' blob:;"
            "media-src 'self' blob: mediastream:;"
            "connect-src 'self' blob: *.revisit.global localhost:3000;"
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
        user = self.current_user_model
        if user:
            return user.name
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

    def _get_current_user_prefs(self):
        """Get the current user's preferences for the templates.

        :return: a json string contain the currently logged in user's prefs.
        """
        prefs = {}
        if self.current_user:
            prefs = self.current_user_model.preferences
        return json_encode(prefs)

    def _t(self, field, default_language):
        """Pick a translation from a translatable field.

        Based on user's preference.

        Falls back to default_language.
        """
        user_language = self.user_default_language
        if user_language and user_language in field:
            return field[user_language]
        return field[default_language]

    def get_template_namespace(self):
        """Template functions.

        TODO: Find a way to get rid of this.
        @jmwohl
        """
        namespace = super().get_template_namespace()
        namespace.update({
            'surveys_for_menu': self._get_surveys_for_menu(),
            'current_user_id': self._get_current_user_id(),
            '_t': self._t,
            'current_user_prefs': self._get_current_user_prefs()
        })
        return namespace

    def write_error(self, status_code, **kwargs):
        """Deal with 404 errors."""
        if 'exc_info' in kwargs and kwargs['exc_info'][0] is NoResultFound:
            self.set_status(404)
            status_code = 404
        if status_code == 404:
            self.render('404.html')
            return
        super().write_error(status_code, **kwargs)


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
