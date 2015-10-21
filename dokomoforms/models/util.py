"""
Useful reusable functions for models.

Models should inherit from dokomforms.models.util.Base, and should almost
certainly make use of the dokomoforms.models.util.pk and
dokomoforms.models.util.last_update_time

The SQLAlchemy documentation suggests setting those columns in the base
class or using class mixins, but it makes it less explicit which columns exist
when looking at the models' definitions.
"""
import abc
import datetime
import json
from collections import OrderedDict
from decimal import Decimal

import sqlalchemy as sa
import sqlalchemy.engine
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func
from sqlalchemy.sql.functions import current_timestamp

from psycopg2.extras import Range

from dokomoforms.options import options
from dokomoforms.exc import NotJSONifiableError


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

    @abc.abstractmethod  # pragma: no cover
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
        instead of a regular dict so that the restless serializer and __str__
        method always return the keys in the same order.
        """

    def __str__(self) -> str:
        """Return the string representation of this model."""
        return (
            json.dumps(self, cls=ModelJSONEncoder, indent=4)
            .replace('</', '<\\/')
        )


sa.event.listen(
    Base.metadata,
    'before_create',
    # Creating extensions in pg_catalog makes them available to the entire
    # database without any prefix.
    sa.DDL(
        'ALTER DATABASE {db} SET TIMEZONE TO "UTC";'
        'CREATE SCHEMA IF NOT EXISTS public;'
        'CREATE SCHEMA IF NOT EXISTS {schema};'
        'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'  # UUID columns
        ' WITH SCHEMA pg_catalog;'
        # 'CREATE EXTENSION IF NOT EXISTS "lo"'  # Large Object (BLOB)
        # ' WITH SCHEMA pg_catalog;'
        'CREATE EXTENSION IF NOT EXISTS "postgis";'  # Geometry columns
        'CREATE EXTENSION IF NOT EXISTS "btree_gist"'  # Exclusion constraints
        ' WITH SCHEMA pg_catalog;'
        .format(db=options.db_database, schema=options.schema)
    ),
)


UUID_REGEX = (
    '[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}'
)


def jsonify(obj, *, raise_exception=False) -> object:
    """Convert the given object to something JSON can handle."""
    if isinstance(obj, Base):
        return obj._asdict()
    if isinstance(obj, bytes):
        return obj.decode()
    if isinstance(obj, (datetime.date, datetime.time)):
        return obj.isoformat()
    if isinstance(obj, Decimal):  # might want to return a string instead
        return float(obj)
    if isinstance(obj, Range):
        left, right = obj._bounds
        return '{}{},{}{}'.format(left, obj.lower, obj.upper, right)

    if raise_exception:
        raise NotJSONifiableError(obj)
    return obj


# Might want to use restless.utils.MoreTypesJSONEncoder as base class
class ModelJSONEncoder(json.JSONEncoder):

    """This JSONEncoder handles the models in dokomoforms.models.

    To use it manually, call:

        json.dumps(
            model, cls=dokomoforms.models.util.ModelJSONEncoder, **kwargs
        )
    """

    def default(self, obj):
        """Handle special types for json.dumps.

        If obj is a model from dokomoforms.models, return a dictionary
        representation.

        If obj is a datetime.date or datetime.time, return an
        ISO 8601 representation string.

        If obj is a psycpg2 Range, return its string representation.

        Otherwise, throw a TypeError.

        See
        https://docs.python.org/3/library/json.html#json.JSONEncoder.default
        """
        try:
            return jsonify(obj, raise_exception=True)
        except NotJSONifiableError:
            return super().default(obj)


def create_engine(pool_size: int=None,
                  max_overflow: int=None,
                  echo: bool=None) -> sqlalchemy.engine.Engine:
    """Get a connection to the database.

    Return a sqlalchemy.engine.Engine configured with the options set in
    dokomoforms.options.options

    :return: a SQLAlchemy engine
    """
    connection_string = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(
        options.db_user,
        options.db_password,
        options.db_host,
        options.db_port,
        options.db_database,
    )
    pool_size = pool_size or options.pool_size
    max_overflow = max_overflow or options.max_overflow
    engine_params = dict()
    if echo is not None:
        engine_params['echo'] = echo
    if pool_size is not None:
        engine_params['pool_size'] = pool_size
    if max_overflow is not None:
        engine_params['max_overflow'] = max_overflow
    return sa.create_engine(connection_string, **engine_params)


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


def languages_column(column_name) -> sa.Column:
    """A TEXT[] column of length > 0.

    Return an ARRAY(TEXT, as_tuple=True) column.

    :param column_name: the name of the column
    :returns: a SQLAlchemy Column for a non-null ARRAY(TEXT, as_tuple=True)
              type.
    """
    return sa.Column(
        pg.ARRAY(pg.TEXT, as_tuple=True),
        sa.CheckConstraint(
            'COALESCE(ARRAY_LENGTH({}, 1), 0) > 0'.format(column_name)
        ),
        nullable=False,
        default=['English'],
    )


def languages_constraint(column_name, languages_column_name) -> sa.Constraint:
    """CHECK CONSTRAINT for a translatable column.

    Checks that all of the languages in the languages column exist as keys in
    the translatable column.

    :param column_name: the name of the translatable column
    :param languages_column_name: the name of the TEXT[] column containing the
                                  languages.
    :return: a SQLAlchemy Constraint to ensure that all the required
             translations are available.
    """
    return sa.CheckConstraint(
        "{} ?& {}".format(column_name, languages_column_name),
        name='all_{}_languages_present_in_{}'.format(
            column_name, languages_column_name
        ),
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


def get_model(session, model_cls, model_id, exception=None):
    """Throw an error if session.query.get(model_id) returns None."""
    model = session.query(model_cls).get(model_id)
    if model is None:
        if exception is None:
            exception = NoResultFound((model_cls, model_id))
        raise exception
    return model


def column_search(query, *,
                  model_cls, column_name, search_term,
                  language=None, regex=False) -> 'query':
    """Modify a query to search a column's values (JSONB or TEXT).

    TODO: document this

    :param query: a
    :param model_cls: aa
    :param column: b
    :param search_term: c
    :param language: d
    :param regex: r
    :return: The modified query.
    """
    column = getattr(model_cls, column_name)
    if not regex:
        search_term = search_term.translate(str.maketrans(
            {'%': '\%', '_': '\_', '\\': r'\\'}
        ))
    # JSONB column
    if str(column.type) == 'JSONB':
        # Search across languages
        if language is None:
            query = (
                query
                .select_from(
                    model_cls, func.jsonb_each_text(column).alias('search')
                )
            )
            if regex:
                return (
                    query.
                    filter(sa.text('search.value ~* :search_term'))
                    .params(search_term=search_term)
                )
            return (
                query
                .filter(sa.text("search.value ILIKE :search_term"))
                .params(search_term='%{}%'.format(search_term))
            )
        # Search for a specific language
        if regex:
            return (
                query
                .filter(sa.text("{}->>:lang ~* :search_term".format(column)))
                .params(lang=language, search_term=search_term)
            )
        return (
            query
            .filter(column[language].astext.ilike('%{}%'.format(search_term)))
        )

    # TEXT column
    if regex:
        return (
            query
            .filter(sa.text('{} ~* :search_term'.format(column)))
            .params(search_term=search_term)
        )
    return (
        query
        .filter(column.ilike('%{}%'.format(search_term)))
    )


def _get_field(model, field_name):
    model_dict = model._asdict()
    try:
        return model_dict[field_name]
    except KeyError:
        return getattr(model, field_name)


def get_fields_subset(model: Base, fields: list) -> OrderedDict:
    """Return the given fields for the model's dictionary representation."""
    return OrderedDict(
        (name, _get_field(model, name)) for name in fields if name
    )
