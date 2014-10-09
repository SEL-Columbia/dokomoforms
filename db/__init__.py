from sqlalchemy import create_engine

from settings import CONNECTION_STRING


engine = create_engine(CONNECTION_STRING, convert_unicode=True)
