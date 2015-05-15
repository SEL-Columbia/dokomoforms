"""Useful reusable functions for models."""

from tornado.options import options
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy import MetaData, Column, DateTime
from sqlalchemy.sql import func


metadata = MetaData(schema=options.schema)
Base = declarative_base(metadata=metadata)


def uuid_generate_v4():
    return getattr(func, '{}.uuid_generate_v4'.format(options.schema))()


def pk():
    return Column(pg.UUID, primary_key=True, server_default=uuid_generate_v4())


def last_update_time():
    return Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
