"""User models"""

from dokomoforms.models import util, Base
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import sqlalchemy as sa


class User(Base):
    __tablename__ = 'auth_user'

    id = util.pk()
    is_active = sa.Column(sa.Boolean, nullable=False, server_default='True')
    name = sa.Column(sa.String, nullable=False)
    token = sa.Column(pg.BYTEA)
    token_expiration = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_update_time = util.last_update_time()


class Email(Base):
    __tablename__ = 'email'

    id = util.pk()
    address = sa.Column(sa.String, nullable=False, unique=True)
    user_id = sa.Column(pg.UUID, sa.ForeignKey('auth_user.id'))
    last_update_time = util.last_update_time()

    user = relationship('User', backref=backref('emails', order_by=id))
