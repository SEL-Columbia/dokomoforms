"""Administrative handlers."""

import tornado.web
import tornado.gen
import tornado.httpclient

from dokomoforms.handlers.util import BaseHandler


class Index(BaseHandler):
    def get(self):
        self.render('administrative/index.html')


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
        self.render('administrative/404.html')
