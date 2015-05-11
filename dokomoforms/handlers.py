"""Index handler"""

import tornado.web
from dokomoforms.models import Question


class BaseHandler(tornado.web.RequestHandler):
    @property
    def session(self):
        return self.application.session


class IndexHandler(BaseHandler):
    def get(self):
        self.session.add(Question(name='aaa'))
        self.write(self.session.query(Question).all())
