"""Define setup and teardown functions for test modules."""

from dokomoforms.options import set_arg
set_arg([None, '--schema=doko_test'])
from sqlalchemy import DDL
from dokomoforms.models import create_engine, Base


engine = create_engine()


def setUpModule():
    Base.metadata.create_all(engine)


def tearDownModule():
    engine.execute(DDL('DROP SCHEMA IF EXISTS doko_test CASCADE'))
