"""
Defines setup and teardown functions for test modules.
Also injects the --schema=doko_test option.
"""
import unittest

from dokomoforms.options import inject_options

inject_options(schema='doko_test')

from sqlalchemy import DDL
from dokomoforms.models import create_engine, Base

engine = create_engine(echo=False)


class DokoTest(unittest.TestCase):
    def setUp(self):
        """Creates the tables in the doko_test schema."""
        Base.metadata.create_all(engine)

    def tearDown(self):
        """Drops the doko_test schema."""
        engine.execute(DDL('DROP SCHEMA IF EXISTS doko_test CASCADE'))
