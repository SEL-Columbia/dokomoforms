"""Submission models."""

from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.ext.orderinglist import ordering_list

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
    enumerator_only = sa.Column(survey_type_enum, nullable=False)
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
    submitter_email = sa.Column(pg.TEXT, nullable=False, server_default='')
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
            ['survey_id', 'enumerator_only'],
            ['survey.id', 'survey.enumerator_only']
        ),
        sa.UniqueConstraint('id', 'enumerator_only'),
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
    __tablename__ = 'submission_public'

    id = util.pk()
    enumerator_user_id = sa.Column(pg.UUID, util.fk('auth_user.id'))
    enumerator = relationship('User')
    should_authenticate = sa.Column(survey_type_enum, nullable=False)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id', 'should_authenticate'],
            ['submission.id', 'submission.enumerator_only']
        ),
        sa.CheckConstraint('NOT should_authenticate::TEXT::BOOLEAN'),
    )

    __mapper_args__ = {'polymorphic_identity': 'unauthenticated'}

    def _asdict(self):
        result = super()._default_asdict()
        if self.enumerator_user_id is not None:
            result['enumerator_user_id'] = self.enumerator_user_id
            result['enumerator_user_name'] = self.enumerator.name
        return result


def construct_submission(*, submission_type: str, **kwargs) -> Submission:
    """
    Returns a subclass of dokomoforms.models.submission.Submission determined
    by the submission_type parameter. This utility function makes it easy to
    create an instance of a Submission subclass based on external
    input.

    See http://stackoverflow.com/q/30518484/1475412

    :param submission_type: the type of submission. Must be either
        'unauthenticated' or 'authenticated'
    :param kwargs: the keyword arguments to pass to the constructor
    :returns: an instance of one of the Node subtypes
    :raises: dokomoforms.exc.NoSuchSubmissionTypeError
    """

    survey_constructor = EnumeratorOnlySubmission

    if submission_type == 'unauthenticated':
        survey_constructor = PublicSubmission

    try:
        return survey_constructor(**kwargs)
    except KeyError:
        raise NoSuchSubmissionTypeError(submission_type)
