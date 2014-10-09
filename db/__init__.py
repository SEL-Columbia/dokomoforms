"""Set up database access."""
from sqlalchemy import create_engine

from settings import CONNECTION_STRING


engine = create_engine(CONNECTION_STRING, convert_unicode=True)

def set_testing_engine(testing_engine):
    """This may or may not work."""
    global engine
    engine = testing_engine
