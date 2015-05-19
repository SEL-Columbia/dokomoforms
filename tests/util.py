"""
Defines setup and teardown functions for test modules.
Also injects the --schema=doko_test option.
"""

from dokomoforms.options import inject_options

inject_options(schema='doko_test')

from sqlalchemy import DDL
from dokomoforms.models import create_engine, Base

engine = create_engine()


def setUpModule():
    """Creates the tables in the doko_test schema."""
    Base.metadata.create_all(engine)


def tearDownModule():
    """Drops the doko_test schema."""
    engine.execute(DDL('DROP SCHEMA IF EXISTS doko_test CASCADE'))
