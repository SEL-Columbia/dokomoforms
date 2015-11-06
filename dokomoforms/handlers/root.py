"""Administrative handlers."""
import tornado.web
import tornado.gen
import tornado.httpclient

from dokomoforms.handlers.util import BaseHandler
from dokomoforms.models import Administrator, User


class Index(BaseHandler):

    """The root URL."""

    def get(self, msg=''):
        """GET /."""
        user = self.current_user_model
        if isinstance(user, Administrator):
            self.redirect('/admin')
            return
        if isinstance(user, User):
            self.redirect('/enumerate')
            return
        self.render(
            'index.html',
            message=msg,
        )


class NotFound(BaseHandler):

    """This is the "default" handler according to Tornado."""

    def prepare(self):
        """
        Raise a 404 for any URL without an explicitly defined handler.

        :raise tornado.web.HTTPError: 404 Not Found
        """
        raise tornado.web.HTTPError(404)

    def write_error(self, *args, **kwargs):
        """Serve the custom 404 page."""
        self.render('404.html')
