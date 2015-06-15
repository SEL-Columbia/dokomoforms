"""Submission models."""

from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import current_timestamp

from dokomoforms.models import util, Base, survey_type_enum


class Submission(Base):
    __tablename__ = 'submission'

    id = util.pk()
    submission_type = sa.Column(
        sa.Enum(
            'unauthenticated', 'authenticated',
            name='submission_type_enum', inherit_schema=True
        ),
        nullable=False,
    )
    survey_id = sa.Column(pg.UUID, nullable=False)
    authenticate_submitter = sa.Column(survey_type_enum, nullable=False)
    save_time = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=current_timestamp(),
    )
    submission_time = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=current_timestamp(),
    )
    submitter_name = sa.Column(pg.TEXT, nullable=False, server_default='')
    submitter_email = sa.Column(pg.TEXT, nullable=False, server_default='')
    last_update_time = util.last_update_time()

    __mapper_args__ = {
        'polymorphic_on': submission_type,
        'polymorphic_identity': 'unauthenticated',
    }
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['survey_id', 'authenticate_submitter'],
            ['survey.id', 'survey.authenticate_submitter']
        ),
        sa.UniqueConstraint('id', 'authenticate_submitter'),
        sa.UniqueConstraint('id', 'survey_id'),
    )

    def _default_asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('deleted', self.deleted),
            ('survey_id', self.survey_id),
            ('save_time', self.save_time),
            ('submission_time', self.submission_time),
            ('last_update_time', self.last_update_time),
            ('submitter_name', self.submitter_name),
            ('submitter_email', self.submitter_email),
        ))


class AuthenticatedSubmission(Submission):
    __tablename__ = 'submission_authenticated'

    id = util.pk()
    the_survey_id = sa.Column(pg.UUID, nullable=False)
    enumerator_user_id = sa.Column(
        pg.UUID, util.fk('auth_user.id'), nullable=False
    )
    enumerator = relationship('User')

    __mapper_args__ = {'polymorphic_identity': 'authenticated'}
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id', 'the_survey_id'], ['submission.id', 'submission.survey_id']
        ),
        sa.ForeignKeyConstraint(
            ['the_survey_id', 'enumerator_user_id'],
            ['enumerator.authentication_required_survey_id',
                'enumerator.user_id']
        ),
    )

    def _asdict(self) -> OrderedDict:
        result = super()._default_asdict()
        result['enumerator_user_id'] = self.enumerator_user_id
        result['enumerator_user_name'] = self.enumerator.name
        return result


class NonAuthenticatedSubmission(Submission):
    __tablename__ = 'submission_non_authenticated'

    id = util.pk()
    should_authenticate = sa.Column(survey_type_enum, nullable=False)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id', 'should_authenticate'],
            ['submission.id', 'submission.authenticate_submitter']
        ),
        sa.CheckConstraint('NOT should_authenticate::TEXT::BOOLEAN'),
    )

    __mapper_args__ = {'polymorphic_identity': 'unauthenticated'}

    def _asdict(self):
        return super()._default_asdict()
