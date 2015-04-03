"""Survey views."""

import tornado.web

from dokomoforms.handlers.util.base import BaseHandler


class ViewHandler(BaseHandler):
    """The endpoint for getting all of a user's surveys."""

    @tornado.web.authenticated
    def get(self):
        self.render('view.html', message=None)
