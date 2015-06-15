"""
Defines setup and teardown functions for test modules.
Also injects the --schema=doko_test option.
"""
import unittest
from urllib.parse import urlencode

from tornado.testing import AsyncHTTPTestCase

from dokomoforms.options import inject_options

inject_options(schema='doko_test')

from sqlalchemy import DDL
from sqlalchemy.orm import sessionmaker
from dokomoforms.models import create_engine, Base
from webapp import Application

engine = create_engine(echo=False)
Session = sessionmaker()


def setUpModule():
    """Creates the tables in the doko_test schema."""
    Base.metadata.create_all(engine)


def tearDownModule():
    """Drops the doko_test schema."""
    engine.execute(DDL('DROP SCHEMA IF EXISTS doko_test CASCADE'))


def load_fixtures():
    """
    Load database fixtures.
    """
    #os.system("psql %s --user=%s --password=%s < %s" % (settings['db_name'],
    #    settings['db_user'], settings['db_password'], settings['db_fixtures_file']))

    #return tornado.database.Connection(
    #    host=settings['db_host'], database=settings['db_name'],
    #    user=settings['db_user'], password=settings['db_password'])
    pass


def unload_fixtures():
    """
    Unload database fixtures.
    """
    #os.system("psql %s --user=%s --password=%s < %s" % (settings['db_name'],
    #    settings['db_user'], settings['db_password'], settings['db_fixtures_file']))

    #return tornado.database.Connection(
    #    host=settings['db_host'], database=settings['db_name'],
    #    user=settings['db_user'], password=settings['db_password'])
    pass


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

    def __init__(self, methodName='runTest', **kwargs):
        super().__init__(methodName=methodName, **kwargs)
        self._api_root = '/api/v0'

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

    def append_query_params(self, url, params_dict):
        """
        Convenience method which url encodes a dict of params
        and appends them to a url with a '?', returning the 
        resulting url.
        """
        params = urlencode(params_dict)
        url += '?' + params
        return url
