"""Administrative handlers."""
from sqlalchemy.sql.functions import count

import tornado.web
import tornado.gen
import tornado.httpclient

from dokomoforms.handlers.util import BaseHandler
from dokomoforms.models import (
    most_recent_surveys, most_recent_submissions,
    User, Administrator, Email
)
from dokomoforms.options import options


class Index(BaseHandler):

    """The root URL."""

    def _no_users(self):
        """Return whether there are no users in the database."""
        return not self.session.query(count(User.id)).scalar()

    def get(self, msg=''):
        """GET /."""
        if options.firstrun and self._no_users():
            self.redirect('/firstrun')
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

    """The URL to visit for configuring the application the first time."""

    def get(self):
        """Display the initial configuration page."""
        self.render('firstrun.html')

    def post(self):
        """Modify the local_config.py file."""
        username = self.get_body_argument('username')
        email = self.get_body_argument('email')
        organization = self.get_body_argument('organization')
        db_password = self.get_body_argument('db_password')
        with self.session.begin():
            self.session.add(
                Administrator(name=username, emails=[Email(address=email)])
            )
        with open('local_config.py', 'a') as local_config:
            local_config.write(
                '# Values set here during initial configuration.\n'
                '###############################################\n'
            )
            local_config.write('firstrun = False\n')
            local_config.write("organization = '{}'\n".format(organization))
            local_config.write("db_password = '{}'\n".format(db_password))
            local_config.write(
                '###############################################\n'
            )
        with self.session.begin():
            self.session.execute(
                "ALTER USER postgres WITH PASSWORD '{}'".format(db_password)
            )
        self.write('Created user and edited local_config.py')


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
