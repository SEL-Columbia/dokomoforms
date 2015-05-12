"""Index handler"""

import tornado.web
from dokomoforms.models import User


class BaseHandler(tornado.web.RequestHandler):
    @property
    def session(self):
        return self.application.session


class IndexHandler(BaseHandler):
    def get(self):
        """Documentation... This isn't a real endpoint"""
        self.session.add(User(name='aaa'))
        self.session.commit()
        self.write(', '.join(q.name for q in self.session.query(User)))
