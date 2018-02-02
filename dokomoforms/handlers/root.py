"""Administrative handlers."""
from datetime import timedelta
from urllib.parse import urlencode
from uuid import uuid4

import tornado.web
import tornado.gen
import tornado.httpclient

from dokomoforms.handlers.portier import redis_kv
from dokomoforms.handlers.util import BaseHandler
from dokomoforms.models import Administrator, User
from dokomoforms.options import options


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


def post(self):

    """Send login information to the portier broker."""

    nonce = uuid4().hex
    redis_kv.setex(nonce, timedelta(minutes=15), '')
    query_args = urlencode({
        'login_hint': self.get_argument('email'),
        'scope': 'openid email',
        'nonce': nonce,
        'response_type': 'id_token',
        'response_mode': 'form_post',
        'client_id': options.minigrid_website_url,
        'redirect_uri': options.minigrid_website_url + '/verify',
    })
    self.redirect('https://broker.portier.io/auth?' + query_args)


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
