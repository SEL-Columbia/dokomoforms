"""Useful reusable functions for models."""

from dokomoforms.options import options, parse_options
parse_options()  # Necessary to load the schema properly
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql as pg
import sqlalchemy as sa
from sqlalchemy.sql import func


metadata = sa.MetaData(schema=options.schema)
Base = declarative_base(metadata=metadata)
sa.event.listen(
    Base.metadata,
    'before_create',
    sa.DDL(
        'CREATE SCHEMA IF NOT EXISTS {};'
        'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'
        ' WITH SCHEMA pg_catalog;'.format(options.schema)
    ),
)


def create_engine():
    return sa.create_engine(
        'postgresql+psycopg2://{}:{}@{}/{}'.format(
            options.db_user,
            options.db_password,
            options.db_host,
            options.db_database,
        ),
        convert_unicode=True,
        pool_size=0,
        max_overflow=-1,
    )


def pk():
    return sa.Column(
        pg.UUID,
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )


def last_update_time():
    return sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
