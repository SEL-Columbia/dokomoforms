"""Submission models."""

from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.ext.orderinglist import ordering_list

from dokomoforms.models import util, Base, survey_type_enum


class Submission(Base):

    """A Submission references a Survey and has a list of Answers."""

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
    survey_type = sa.Column(survey_type_enum, nullable=False)
    save_time = sa.Column(
        pg.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=current_timestamp(),
    )
    submission_time = sa.Column(
        pg.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=current_timestamp(),
    )
    submitter_name = sa.Column(pg.TEXT, nullable=False, server_default='')
    submitter_email = sa.Column(
        pg.TEXT, sa.CheckConstraint("submitter_email ~ '^$|.*@.*'"),
        nullable=False, server_default=''
    )
    answers = relationship(
        'Answer',
        order_by='Answer.answer_number',
        collection_class=ordering_list('answer_number'),
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    last_update_time = util.last_update_time()

    __mapper_args__ = {
        'polymorphic_on': submission_type,
    }
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['survey_id', 'survey_type'],
            ['survey.id', 'survey.survey_type']
        ),
        sa.UniqueConstraint('id', 'survey_type'),
        sa.UniqueConstraint('id', 'survey_id'),
        sa.UniqueConstraint('id', 'submission_time', 'survey_id'),
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
            ('answers', [answer.response for answer in self.answers]),
        ))


class EnumeratorOnlySubmission(Submission):

    """An EnumeratorOnlySubmission must have an enumerator.

    Use an EnumeratorOnlySubmission for an EnumeratorOnlySurvey.
    """

    __tablename__ = 'submission_enumerator_only'

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
            ['enumerator.enumerator_only_survey_id', 'enumerator.user_id']
        ),
    )

    def _asdict(self) -> OrderedDict:
        result = super()._default_asdict()
        result['enumerator_user_id'] = self.enumerator_user_id
        result['enumerator_user_name'] = self.enumerator.name
        return result


class PublicSubmission(Submission):

    """A PublicSubmission might have an enumerator.

    Use a PublicSubmission for a Survey.
    """

    __tablename__ = 'submission_public'

    id = util.pk()
    enumerator_user_id = sa.Column(pg.UUID, util.fk('auth_user.id'))
    enumerator = relationship('User')
    survey_type = sa.Column(survey_type_enum, nullable=False)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id', 'survey_type'],
            ['submission.id', 'submission.survey_type']
        ),
        sa.CheckConstraint("survey_type::TEXT = 'public'"),
    )

    __mapper_args__ = {'polymorphic_identity': 'unauthenticated'}

    def _asdict(self):
        result = super()._default_asdict()
        if self.enumerator_user_id is not None:
            result['enumerator_user_id'] = self.enumerator_user_id
            result['enumerator_user_name'] = self.enumerator.name
        return result
