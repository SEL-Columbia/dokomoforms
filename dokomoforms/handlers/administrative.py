"""Administrative handlers."""

import tornado.web
import tornado.gen
import tornado.httpclient

from dokomoforms.handlers.util import BaseHandler


class Index(BaseHandler):
    def get(self):
        """Documentation... This isn't a real endpoint"""
        self.render('administrative/index.html')


class NotFound(BaseHandler):
    def prepare(self):
        raise tornado.web.HTTPError(404)

    def write_error(self, *args, **kwargs):
        self.render('administrative/404.html')
