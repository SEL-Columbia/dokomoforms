"""
Useful reusable functions for models.

Models should inherit from dokomforms.models.util.Base, and should almost
certainly make use of the dokomoforms.models.util.pk and
dokomoforms.models.util.last_update_time

The SQLAlchemy documentation suggests setting those columns in the base
class or using class mixins, but it makes it less explicit which columns exist
when looking at the models' definitions.
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


def pk(foreign_key_column_name: str=None) -> sa.Column:
    """
    Returns a standard primary key of type UUID for use in models. If the
    optional foreign_key_column_name is supplied, the primary key will
    reference the given column.

    :param foreign_key_column_name: the column name of the referenced foreign
                                    key (should be 'table_name.column_name')
    :return: a SQLAlchemy Column for a UUID primary key.
    """
    args = [pg.UUID]
    if foreign_key_column_name is not None:
        args.append(fk(foreign_key_column_name))
    kwargs = {
        'primary_key': True,
        'server_default': func.uuid_generate_v4(),
    }
    return sa.Column(*args, **kwargs)


def fk(column_name: str) -> sa.Column:
    """
    Returns a foreign key of type UUID for use in models.

    :param column_name: the name of the referenced column
    :return: a SQLAlchemy Column for a UUID primary key.
    """
    return sa.ForeignKey(column_name, onupdate='CASCADE', ondelete='CASCADE')


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
