"""User models."""

from collections import OrderedDict

from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import current_timestamp
import sqlalchemy as sa

from dokomoforms.models import util, Base


class User(Base):
    """Models a user. A user has at least one e-mail address."""
    __tablename__ = 'auth_user'

    id = util.pk()
    name = sa.Column(pg.TEXT, nullable=False)
    emails = relationship(
        'Email',
        order_by='Email.address',
        backref='user',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    role = sa.Column(
        sa.Enum(
            'enumerator', 'creator', name='user_roles', inherit_schema=True
        ),
        nullable=False,
    )
    last_update_time = util.last_update_time()

    __mapper_args__ = {
        'polymorphic_identity': 'enumerator',
        'polymorphic_on': role,
    }

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('deleted', self.deleted),
            ('name', self.name),
            ('emails', [email.address for email in self.emails]),
            ('role', self.role),
            ('allowed_surveys', self.allowed_surveys),
            ('last_update_time', self.last_update_time),
        ))


class SurveyCreator(User):
    """
    Regular users can answer surveys, but only SurveyCreator instances can
    create surveys.
    """
    __tablename__ = 'survey_creator'

    id = util.pk('auth_user.id')
    surveys = relationship(
        'Survey',
        order_by='Survey.created_on',
        backref='creator',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    token = sa.Column(pg.BYTEA)
    token_expiration = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=current_timestamp(),
    )

    __mapper_args__ = {'polymorphic_identity': 'creator'}

    def _asdict(self) -> OrderedDict:
        result = super()._asdict()
        result['surveys'] = OrderedDict(
            (survey.title, survey.id) for survey in self.surveys
        )
        result['token_expiration'] = self.token_expiration
        return result


class Email(Base):
    """Models an e-mail address."""
    __tablename__ = 'email'

    id = util.pk()
    address = sa.Column(pg.TEXT, nullable=False, unique=True)
    user_id = sa.Column(pg.UUID, util.fk('auth_user.id'), nullable=False)
    last_update_time = util.last_update_time()

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('address', self.address),
            ('user', self.user.name),
            ('last_update_time', self.last_update_time),
        ))
