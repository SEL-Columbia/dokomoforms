"""Test utilities.

Defines setup and teardown functions for test modules.
Also injects the --schema=doko_test option.
"""
from contextlib import contextmanager
from functools import wraps
import unittest
from unittest.mock import patch
from urllib.parse import urlencode

from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase
from tornado.web import RequestHandler

from dokomoforms.options import inject_options, parse_options

inject_options(schema='doko_test')
parse_options()

from dokomoforms.options import options

from sqlalchemy import DDL
from sqlalchemy.orm import sessionmaker
from dokomoforms.models import create_engine, Base
from dokomoforms.handlers.util import BaseHandler
from webapp import Application
from tests.python.fixtures import load_fixtures, unload_fixtures

engine = create_engine(pool_size=0, max_overflow=-1)
Session = sessionmaker()


def setUpModule():
    """Create the tables in the doko_test schema."""
    engine.execute(DDL('DROP SCHEMA IF EXISTS doko_test CASCADE'))
    try:
        Base.metadata.create_all(engine)
    except Exception:
        engine.execute(DDL('DROP SCHEMA IF EXISTS doko_test CASCADE'))
        raise


def tearDownModule():
    """Drop the doko_test schema."""
    engine.execute(DDL('DROP SCHEMA IF EXISTS doko_test CASCADE'))


class DokoTest(unittest.TestCase):

    """Tests that subclass DokoTest happen in a database transaction.

    Since subtransactions don't exactly work under this scheme, if you need
    to access the database after a rollback (e.g., an exception happens),
    you need to use the dont_run_in_a_transaction decorator.
    """

    def setUp(self):
        """Start a transaction."""
        self.connection = engine.connect()
        self.transaction = self.connection.begin()
        self.session = Session(bind=self.connection, autocommit=True)
        super().setUp()

    def tearDown(self):
        """Roll back the transaction."""
        self.session.close()
        self.transaction.rollback()
        self.connection.close()
        super().tearDown()


@contextmanager
def dummy_patch():
    """A context manager that doesn't do anything.

    Also, you can set any attribute on it.
    """
    yield lambda: None


class DokoExternalDBTest(DokoTest):

    """Tests in which the database is being accessed externally.

    Use this for Selenium testing.
    """

    def setUp(self):
        """Load the fixtures."""
        unload_fixtures(engine, 'doko_test')
        load_fixtures(engine)
        self.session = Session(bind=engine, autocommit=True)

    def tearDown(self):
        """Truncate all the tables."""
        unload_fixtures(engine, 'doko_test')
        self.session.close()


class DokoFixtureTest(DokoTest):

    """Tests with fixtures."""

    @classmethod
    def setUpClass(cls):
        """Load the fixtures."""
        load_fixtures(engine)

    def setUp(self):
        """Load the fixtures if necessary."""
        connection = engine.connect()
        with connection.begin():
            anything = (
                connection
                .execute('select count(id) from doko_test.survey;')
                .scalar()
            )
        if not anything:
            self.__class__.setUpClass()
        super().setUp()

    @classmethod
    def tearDownClass(cls):
        """Truncate all the tables."""
        unload_fixtures(engine, 'doko_test')


class DokoHTTPTest(DokoFixtureTest, LogTrapTestCase, AsyncHTTPTestCase):

    """Base class for HTTP (i.e. API [and handler?]) test cases.

    TODO: maybe need to override setUp to log the user in?
    Or this could happen in setUpModule?
    """

    _api_root = '/api/v0'

    @property
    def api_root(self):
        """The API URL up to the version."""
        return '/api/' + self.get_app()._api_version

    def get_app(self):
        """Return an instance of the application to be tested."""
        options.https = True
        options.debug = True
        options.demo = False
        self.app = Application(self.session, options=options)
        return self.app

    def append_query_params(self, url, params_dict):
        """Add parameters from a dict to the URL.

        Convenience method which url encodes a dict of params
        and appends them to a url with a '?', returning the
        resulting url.
        """
        params = urlencode(params_dict)
        url += '?' + params
        return url

    def fetch(self, *args,
              _disable_xsrf: bool=True,
              _logged_in_user: str='b7becd02-1a3f-4c1d-a0e1-286ba121aef4',
              **kwargs):
        """Fetch, circumventing XSRF cookies and logging in (by default)."""
        patch_xsrf = dummy_patch()
        if _disable_xsrf:
            patch_xsrf = patch.object(RequestHandler, 'check_xsrf_cookie')

        patch_login = dummy_patch()
        if _logged_in_user:
            patch_login = patch.object(BaseHandler, '_current_user_cookie')

        with patch_xsrf as x, patch_login as y:
            x.return_value = None
            y.return_value = _logged_in_user
            return super().fetch(*args, **kwargs)


def dont_run_in_a_transaction(doko_test):
    """Use this to perform a test without a surrounding transaction.

    Use this if a test needs to access the database after a rollback, for
    instance.
    """
    @wraps(doko_test)
    def wrapper(self):
        try:
            self.session.close()
            self.session = Session(bind=engine, autocommit=True)
            return doko_test(self)
        finally:
            unload_fixtures(engine, 'doko_test')
            self.session.close()
    return wrapper
