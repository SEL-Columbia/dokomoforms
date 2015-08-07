"""Test utilities.

Defines setup and teardown functions for test modules.
Also injects the --schema=doko_test option.
"""
from contextlib import contextmanager
from functools import wraps
import signal
import sys
import unittest
from unittest.mock import patch
from urllib.parse import urlencode

from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase
from tornado.web import RequestHandler
from tornado.escape import json_encode

from dokomoforms.options import inject_options, parse_options

inject_options(schema='doko_test', debug='True')
parse_options()

from sqlalchemy import DDL
from sqlalchemy.orm import sessionmaker
from dokomoforms.models import create_engine, Base
from dokomoforms.handlers.util import BaseHandler
from webapp import Application
from tests.fixtures import load_fixtures, unload_fixtures

engine = create_engine(echo=False)
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


def keyboard_interrupt_handler(signal, frame):
    """Couldn't find a better solution than this one."""
    sys.exit()


signal.signal(signal.SIGINT, keyboard_interrupt_handler)


class DokoTest(unittest.TestCase):

    """Tests that subclass DokoTest happen in a database transaction.

    Since subtransactions don't exactly work under this scheme, if you need
    to access the database after a rollback (e.g., an exception happens),
    you need to use the test_continues_after_rollback decorator.
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


class DokoHTTPTest(DokoTest, LogTrapTestCase, AsyncHTTPTestCase):

    """Base class for HTTP (i.e. API [and handler?]) test cases.

    TODO: maybe need to override setUp to log the user in?
    Or this could happen in setUpModule?
    """

    _api_root = '/api/v0'

    @property
    def api_root(self):
        """The API URL up to the version."""
        return '/api/' + self.get_app()._api_version

    @classmethod
    def setUpClass(cls):
        """Load the fixtures."""
        load_fixtures(engine)

    @classmethod
    def tearDownClass(cls):
        """Truncate all the tables."""
        unload_fixtures(engine, 'doko_test')

    def get_app(self):
        """Return an instance of the application to be tested."""
        self.app = Application(self.session)
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
              _logged_in_user: dict={
                  'user_id': 'b7becd02-1a3f-4c1d-a0e1-286ba121aef4',
                  'user_name': 'test_user',
              },
              **kwargs):
        """Fetch, circumventing XSRF cookies and logging in (by default)."""
        patch_xsrf = dummy_patch()
        if _disable_xsrf:
            patch_xsrf = patch.object(RequestHandler, 'check_xsrf_cookie')

        patch_login = dummy_patch()
        if _logged_in_user:
            _logged_in_user = json_encode(_logged_in_user)
            patch_login = patch.object(BaseHandler, '_current_user_cookie')

        with patch_xsrf as x, patch_login as l:
            x.return_value = None
            l.return_value = _logged_in_user
            return super().fetch(*args, **kwargs)


def test_continues_after_rollback(doko_test):
    """Use this if a test needs to access the database after a rollback."""
    @wraps(doko_test)
    def wrapper(self):
        self.session.close()
        self.session = Session(bind=engine, autocommit=True)
        try:
            return doko_test(self)
        finally:
            connection = engine.connect()
            with connection.begin():
                connection.execute(
                    """
                    DO
                    $func$
                    BEGIN
                      EXECUTE (
                        SELECT 'TRUNCATE TABLE '
                          || string_agg(
                               'doko_test.' || quote_ident(t.tablename), ', '
                             )
                          || ' CASCADE'
                        FROM   pg_tables t
                        WHERE  t.schemaname = 'doko_test'
                      );
                    END
                    $func$;
                    """
                )
            self.session.close()
    return wrapper
