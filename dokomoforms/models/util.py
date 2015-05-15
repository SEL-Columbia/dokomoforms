"""Useful reusable functions for models."""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy import Column, DateTime, event, DDL
from sqlalchemy.sql import func


class Base(object):
    __table_args__ = {'schema': 'doko'}


Base = declarative_base(cls=Base)
# TODO: Is this the right way to do this?
event.listen(
    Base.metadata,
    'before_create',
    DDL('CREATE SCHEMA IF NOT EXISTS doko'),
)


def pk():
    return Column(
        pg.UUID,
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )


def last_update_time():
    return Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
