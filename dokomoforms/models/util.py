"""Useful reusable functions for models."""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

Base = declarative_base()


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
