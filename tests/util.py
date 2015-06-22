"""
Defines setup and teardown functions for test modules.
Also injects the --schema=doko_test option.
"""

import unittest
from urllib.parse import urlencode

from tornado.testing import AsyncHTTPTestCase
import tornado.ioloop
from functools import wraps

from dokomoforms.options import inject_options

inject_options(schema='doko_test', debug='true')

from sqlalchemy import DDL
from sqlalchemy.orm import sessionmaker
from dokomoforms.models import create_engine, Base
from webapp import Application
from tests.fixtures import load_fixtures, unload_fixtures
from dokomoforms.handlers import DebugLoginHandler

engine = create_engine(echo=False)
Session = sessionmaker()


def setUpModule():
    """Creates the tables in the doko_test schema."""
    engine.execute(DDL('DROP SCHEMA IF EXISTS doko_test CASCADE'))
    try:
        Base.metadata.create_all(engine)
    except Exception:
        engine.execute(DDL('DROP SCHEMA IF EXISTS doko_test CASCADE'))
        raise


def tearDownModule():
    """Drops the doko_test schema."""
    engine.execute(DDL('DROP SCHEMA IF EXISTS doko_test CASCADE'))


class DokoTest(unittest.TestCase):
    def setUp(self):
        """Starts a transaction"""
        self.connection = engine.connect()
        self.transaction = self.connection.begin()
        self.session = Session(bind=self.connection, autocommit=True)

    def tearDown(self):
        """Rolls back the transaction"""
        self.session.close()
        self.transaction.rollback()
        self.connection.close()


class DokoHTTPTest(AsyncHTTPTestCase):
    """
    A base class for HTTP (i.e. API [and handler?]) test cases.

    TODO: maybe need to override setUp to log the user in?
    Or this could happen in setUpModule?
    """

    _api_root = '/api/v0'

    @property
    def api_root(self):
        return '/api/' + self.get_app()._api_version

    def setUp(self):
        """Insert test data"""
        super().setUp()
        load_fixtures()

    def tearDown(self):
        """Remove test data"""
        super().tearDown()
        unload_fixtures()

    def get_app(self):
        """
        Returns an instance of the application to be tested.
        """

        return Application()

    def login(self, user_email):
        # url to test
        url = '/debug/login/' + user_email
        # http method (just for clarity)
        method = 'GET'
        # make login request
        self.fetch(url, method=method)

    def append_query_params(self, url, params_dict):
        """
        Convenience method which url encodes a dict of params
        and appends them to a url with a '?', returning the
        resulting url.
        """
        params = urlencode(params_dict)
        url += '?' + params
        return url


def test_continues_after_rollback(doko_test):
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
                    '''
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
                    '''
                )
            self.session.close()
    return wrapper
