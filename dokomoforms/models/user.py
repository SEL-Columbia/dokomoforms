"""User models."""

from collections import OrderedDict

from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import sqlalchemy as sa

from dokomoforms.models import util, Base


class User(Base):
    """Models a user. A user has at least one e-mail address."""
    __tablename__ = 'auth_user'

    id = util.pk()
    is_active = sa.Column(sa.Boolean, nullable=False, server_default='True')
    name = sa.Column(pg.TEXT, nullable=False)
    token = sa.Column(pg.BYTEA)
    token_expiration = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_update_time = util.last_update_time()

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('is_active', self.is_active),
            ('name', self.name),
            ('emails', [email.address for email in self.emails]),
            ('token_expiration', self.token_expiration),
            ('last_update_time', self.last_update_time),
        ))


class Email(Base):
    """Models an e-mail address."""
    __tablename__ = 'email'

    id = util.pk()
    address = sa.Column(pg.TEXT, nullable=False, unique=True)
    user_id = sa.Column(pg.UUID, util.fk('auth_user.id'), nullable=False)
    last_update_time = util.last_update_time()

    user = relationship('User', backref=backref('emails', order_by=address))

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('address', self.address),
            ('user', self.user.name),
            ('last_update_time', self.last_update_time),
        ))
