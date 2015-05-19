"""
Useful reusable functions for models.

Models should inherit from dokomforms.models.util.Base, and should almost
certainly make use of the dokomoforms.models.util.pk and
dokomoforms.models.util.last_update_time

The SQLAlchemy documentation suggests setting those columns in the base
class but it makes it less explicit which columns exist when looking at the
models' definitions.
"""
from dokomoforms.options import options, parse_options

parse_options()  # Necessary to load the schema properly

import sqlalchemy as sa
import sqlalchemy.engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.sql import func

metadata = sa.MetaData(schema=options.schema)

Base = declarative_base(metadata=metadata)
sa.event.listen(
    Base.metadata,
    'before_create',
    # Creating extensions in pg_catalog makes them available to the entire
    # database without any prefix.
    sa.DDL(
        'CREATE SCHEMA IF NOT EXISTS {schema};'
        'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'
        ' WITH SCHEMA pg_catalog;'.format(schema=options.schema)
    ),
)


def create_engine() -> sqlalchemy.engine.Engine:
    """
    Returns a sqlalchemy.engine.Engine configured with the options set in
    dokomoforms.options.options

    :return: a SQLAlchemy engine
    """
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


def pk() -> sa.Column:
    """
    Returns a standard primary key of type UUID for use in models.

    :return: a SQLAlchemy Column for a UUID primary key.
    """
    return sa.Column(
        pg.UUID,
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )


def last_update_time() -> sa.Column:
    """
    Returns a column containing the time that a record was last updated.

    :return: a SQLAlchemy Column for a datetime with time zone auto-updating
             column
    """
    return sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
