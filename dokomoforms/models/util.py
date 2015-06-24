"""
Useful reusable functions for models.

Models should inherit from dokomforms.models.util.Base, and should almost
certainly make use of the dokomoforms.models.util.pk and
dokomoforms.models.util.last_update_time

The SQLAlchemy documentation suggests setting those columns in the base
class or using class mixins, but it makes it less explicit which columns exist
when looking at the models' definitions.
"""
from dokomoforms.options import options

import abc
import datetime
import json

import sqlalchemy as sa
import sqlalchemy.engine
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.sql import func
from sqlalchemy.sql.functions import current_timestamp

metadata = sa.MetaData(schema=options.schema)


class _Meta(DeclarativeMeta, abc.ABCMeta):

    """Metaclass for dokomoforms.models.Base.

    This is the sqlalchemy.ext.declarative.DeclarativeMeta metaclass with the
    abstract base class metaclass mixed in. It allows
    dokomoforms.models.util.Base to be an abstract class.

    Thanks to http://stackoverflow.com/a/30402243/1475412
    """


class Base(declarative_base(metadata=metadata, metaclass=_Meta)):

    """The base class for all Dokomo Forms models."""

    __abstract__ = True

    deleted = sa.Column(sa.Boolean, nullable=False, server_default='false')

    @abc.abstractmethod
    def _asdict(self) -> dict:
        """Return a dictionary representation of the model.

        Model classes must implement this method to return a dictionary
        representation. If a value is itself a model or a list of models, take
        care to replace it with some other representation to avoid infinite
        recursion. For instance:

            class User(Base):
                __tablename__ = 'auth_user'
                id = util.pk()
                name = sqlalchemy.Column(TEXT)
                emails = relationship(
                    'Email',
                    backref='user',
                    cascade='all, delete-orphan',
                    passive_deletes=True,
                )

            class Email(Base):
                __tablename__ = 'email'
                id = util.pk()
                address = sqlalchemy.Column(TEXT)

        In this scenario, User.emails is a list of Email models and Email.user
        is a User model. So User._asdict should return something like
            'emails': [email.address for email in self.emails],

        In addition, consider returning an instance of collections.OrderedDict
        instead of a regular dict so that the _to_json and __str__ methods
        always return the keys in the same order.
        """
        pass

    def _to_json(self, tornado_encode: bool=True, **kwargs) -> str:
        """Return the JSON representation of this model.

        See dokomoforms.models.util.Base._asdict and
        dokomoforms.models.util.ModelJSONEncoder

        :param tornado_encode: if True, also escapes the forward slash in any
                               occurences of '</' in the JSON string. This is
                               the behavior of tornado.escape.json_encode.
                               Default True
        :param kwargs: any keyword arguments that json.dumps accepts
        """
        result = json.dumps(self, cls=ModelJSONEncoder, **kwargs)
        if tornado_encode:
            return result.replace('</', '<\\/')
        return result

    def __str__(self) -> str:
        """Return the string representation of this model."""
        return self._to_json(tornado_encode=False, indent=4)


sa.event.listen(
    Base.metadata,
    'before_create',
    # Creating extensions in pg_catalog makes them available to the entire
    # database without any prefix.
    sa.DDL(
        'CREATE SCHEMA IF NOT EXISTS public;'
        'CREATE SCHEMA IF NOT EXISTS {schema};'
        'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'  # UUID columns
        ' WITH SCHEMA pg_catalog;'
        # 'CREATE EXTENSION IF NOT EXISTS "lo"'  # Large Object (BLOB)
        # ' WITH SCHEMA pg_catalog;'
        'CREATE EXTENSION IF NOT EXISTS "postgis";'  # Geometry columns
        'CREATE EXTENSION IF NOT EXISTS "btree_gist"'  # Exclusion constraints
        ' WITH SCHEMA pg_catalog;'
        .format(schema=options.schema)
    ),
)


class ModelJSONEncoder(json.JSONEncoder):

    """
    This JSONEncoder knows what to do with the models in dokomoforms.models.

    It is used internally by the _to_json method of any of the model classes.

    To use it manually, call:

        json.dumps(
            model, cls=dokomoforms.models.util.ModelJSONEncoder, **kwargs
        )
    """

    def default(self, obj):
        """Handle special types for json.dumps.

        If obj is a model from dokomoforms.models, return a dictionary
        representation. If obj is a datetime.date or datetime.time, return an
        ISO 8601 representation string. Otherwise, throw a TypeError.

        See
        https://docs.python.org/3/library/json.html#json.JSONEncoder.default
        """
        if isinstance(obj, Base):
            return obj._asdict()
        if isinstance(obj, (datetime.date, datetime.time)):
            return obj.isoformat()
        return super().default(obj)


def create_engine(echo: bool=None) -> sqlalchemy.engine.Engine:
    """Get a connection to the database.

    Return a sqlalchemy.engine.Engine configured with the options set in
    dokomoforms.options.options

    :param echo: whether to print to the command line all of the SQL generated
                 by SQLAlchemy. Defaults to None, which defers to the
                 options.debug setting. Setting this parameter to True or False
                 (or 'debug') overrides the echo setting of options.debug.
    :return: a SQLAlchemy engine
    """
    if echo is None:
        # This causes duplicate log messages, but I can't figure out how to get
        # the same level of logging otherwise...
        echo = 'debug' if options.debug else False
    return sa.create_engine(
        'postgresql+psycopg2://{}:{}@{}/{}'.format(
            options.db_user,
            options.db_password,
            options.db_host,
            options.db_database,
        ),
        # pool_size=0,
        # max_overflow=-1,
        echo=echo,
    )


def pk(*foreign_key_column_names: str) -> sa.Column:
    """A UUID primary key.

    Return a standard primary key of type UUID for use in models. If the
    any foreign_key_column_names are supplied, the primary key will
    reference the given columns.

    :param foreign_key_column_names: column names of the referenced foreign
                                    keys (should be 'table_name.column_name')
    :return: a SQLAlchemy Column for a UUID primary key.
    """
    args = [pg.UUID]
    args.extend(map(fk, foreign_key_column_names))
    kwargs = {
        'primary_key': True,
        'server_default': func.uuid_generate_v4(),
    }
    return sa.Column(*args, **kwargs)


def fk(column_name: str) -> sa.Column:
    """A foreign key with ONUPDATE CASCADE and ONDELETE CASCADE.

    Return a foreign key of type UUID for use in models.

    The relationship CASCADEs on UPDATE and DELETE.

    :param column_name: the name of the referenced column
    :return: a SQLAlchemy Column for a UUID primary key.
    """
    return sa.ForeignKey(column_name, onupdate='CASCADE', ondelete='CASCADE')


def json_column(column_name: str, *, default=None) -> sa.Column:
    """A JSONB column.

    Return a column of type JSONB for use in models. Use this for entries like

        <language>: <text>

    :param column_name: the name of the column
    :param default: the column default (default value None, meaning no column
                    default)
    :return: a SQLAlchemy Column for a non-null JSONB type.
    """
    return sa.Column(
        pg.json.JSONB,
        sa.CheckConstraint(
            "{} @> '{{}}'".format(column_name),
            name='{}_valid_json_check'.format(column_name),
        ),
        nullable=False,
        server_default=default,
    )


def last_update_time() -> sa.Column:
    """A timestamp column set to CURRENT_TIMESTAMP on update.

    Return a column containing the time that a record was last updated.

    :return: a SQLAlchemy Column for a datetime with time zone auto-updating
             column
    """
    return sa.Column(
        pg.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=current_timestamp(),
        onupdate=current_timestamp(),
    )
