"""
Defines setup and teardown functions for test modules.
Also injects the --schema=doko_test option.
"""

import unittest
from functools import wraps

from dokomoforms.options import inject_options

inject_options(schema='doko_test')

from sqlalchemy import DDL
from sqlalchemy.orm import sessionmaker
from dokomoforms.models import create_engine, Base

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
