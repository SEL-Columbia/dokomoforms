"""Administrative handlers."""
from sqlalchemy.sql.functions import count

import tornado.web
import tornado.gen
import tornado.httpclient

from dokomoforms.handlers.util import BaseHandler
from dokomoforms.models import (
    most_recent_surveys, most_recent_submissions, User
)
from dokomoforms.options import options


class Index(BaseHandler):

    """The root URL."""

    def get(self, msg=''):
        """GET /."""
        if options.firstrun:
            self.redirect('firstrun')
            return
        surveys = None
        recent_submissions = None
        current_user_id = None
        if self.current_user:
            surveys = most_recent_surveys(
                self.session, current_user_id, 10
            )
            recent_submissions = most_recent_submissions(
                self.session, current_user_id, 5
            )
        self.render(
            'index.html',
            message=msg,
            surveys=surveys,
            recent_submissions=recent_submissions
        )

class FirstRun(BaseHandler):

    """The URL to visit for configurating the application the first time."""

    def get(self):
        if self.session.query(count(User.id)).scalar():
            pass  # there are users, firstun is invalid
        pass  # write the html

    def post(self):
        pass  # edit local_config.py

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
