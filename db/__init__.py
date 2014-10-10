"""Set up database access."""
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from settings import CONNECTION_STRING


engine = create_engine(CONNECTION_STRING, convert_unicode=True)


def set_testing_engine(testing_engine: Engine):
    """
    Use this function to set an alternate testing engine (like SQLite):

    import db

    from sqlalchemy import create_engine

    db.set_engine(create_engine(CONNECTION_STRING, convert_unicode=True))

    :param testing_engine: A SQLAlchemy engine
    """
    global engine
    engine = testing_engine
