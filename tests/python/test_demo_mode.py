"""Demo mode tests."""
from sqlalchemy.sql.functions import count

from tests.python.util import (
    DokoHTTPTest, setUpModule, tearDownModule
)

utils = (setUpModule, tearDownModule)

from dokomoforms.models import Administrator
from dokomoforms.options import options

from webapp import Application


class TestDemoMode(DokoHTTPTest):
    def get_app(self):
        options.debug = False
        options.demo = True
        self.app = Application(self.session, options=options)
        return self.app

    def test_logging_in_creates_user(self):
        no_user = (
            self.session
            .query(count(Administrator.id))
            .filter_by(name='demo_user')
            .scalar()
        )
        self.assertEqual(no_user, 0)
        self.fetch('/demo/login', _logged_in_user=None)
        user = (
            self.session
            .query(count(Administrator.id))
            .filter_by(name='demo_user')
            .scalar()
        )
        self.assertEqual(user, 1)

    def test_logout(self):
        response = self.fetch(
            '/demo/logout', _logged_in_user=None, follow_redirects=False
        )
        self.assertEqual(response.code, 302)
