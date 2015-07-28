"""Administrative handlers."""

import tornado.web
import tornado.gen
import tornado.httpclient

from dokomoforms.handlers.util import BaseHandler
from dokomoforms.models import Survey, Submission


class Index(BaseHandler):

    """The root URL."""

    def get(self, msg=''):
        """GET /."""
        surveys = None
        recent_submissions = None
        if self.current_user:
            surveys = (
                self.session
                .query(Survey)
                .filter_by(creator_id=self.current_user_model.id)
                .order_by(Survey.created_on.desc())
                .limit(10)
            )
            recent_submissions = (
                self.session
                .query(Submission)
                .join(Survey)
                .filter_by(creator_id=self.current_user_model.id)
                .order_by(Submission.save_time.desc())
                .limit(5)
            )
        self.render(
            'index.html',
            message=msg,
            surveys=surveys,
            recent_submissions=recent_submissions,
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
