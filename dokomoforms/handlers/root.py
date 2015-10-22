"""Administrative handlers."""
import tornado.web
import tornado.gen
import tornado.httpclient

from dokomoforms.handlers.util import BaseHandler
from dokomoforms.models import most_recent_surveys


class Index(BaseHandler):

    """The root URL."""

    def get(self, msg=''):
        """GET /."""
        surveys = None
        current_user_id = None
        if self.current_user:
            current_user_id = self.current_user_model.id
            surveys = most_recent_surveys(
                self.session, current_user_id, 10
            )
        self.render(
            'index.html',
            message=msg,
            surveys=surveys,
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
