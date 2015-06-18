"""Answer models."""

import abc
from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship, synonym
from sqlalchemy.ext.hybrid import hybrid_property
# from sqlalchemy.sql.type_api import UserDefinedType

from geoalchemy2 import Geometry

from dokomoforms.models import util, Base, node_type_enum
from dokomoforms.exc import NoSuchNodeTypeError


class Answer(Base):
    __tablename__ = 'answer'

    id = util.pk()
    answer_number = sa.Column(sa.Integer, nullable=False)
    submission_id = sa.Column(pg.UUID, nullable=False)
    submission_time = sa.Column(pg.TIMESTAMP(timezone=True), nullable=False)
    survey_id = sa.Column(pg.UUID, nullable=False)
    survey_node_id = sa.Column(pg.UUID, nullable=False)
    survey_node = relationship('AnswerableSurveyNode')
    allow_multiple = sa.Column(sa.Boolean, nullable=False)
    allow_other = sa.Column(sa.Boolean, nullable=False)
    allow_dont_know = sa.Column(sa.Boolean, nullable=False)
    question_id = sa.Column(pg.UUID, nullable=False)
    type_constraint = sa.Column(node_type_enum, nullable=False)
    last_update_time = util.last_update_time()

    @property
    @abc.abstractmethod
    def main_answer(self):
        pass

    @property
    @abc.abstractmethod
    def answer(self):
        pass

    @property
    @abc.abstractmethod
    def other(self):
        pass

    @property
    @abc.abstractmethod
    def dont_know(self):
        pass

    @hybrid_property
    def response(self) -> OrderedDict:
        possible_responses = [
            ('answer', self.main_answer),
            ('other', self.other),
            ('dont_know', self.dont_know),
        ]
        response_type, response = next(
            p_r for p_r in possible_responses if p_r[1] is not None
        )
        if response_type == 'answer':
            response = self.answer
        return OrderedDict((
            ('response_type', response_type),
            ('response', response),
        ))

    __mapper_args__ = {'polymorphic_on': type_constraint}
    __table_args__ = (
        sa.UniqueConstraint('id', 'allow_other', 'allow_dont_know'),
        sa.UniqueConstraint(
            'id', 'allow_other', 'allow_dont_know', 'survey_node_id',
            'question_id', 'submission_id',
        ),
        sa.ForeignKeyConstraint(
            ['submission_id', 'submission_time', 'survey_id'],
            ['submission.id', 'submission.submission_time',
                'submission.survey_id']
        ),
        sa.ForeignKeyConstraint(
            [
                'survey_node_id',
                'question_id',
                'type_constraint',
                'allow_multiple',
                'allow_other',
                'allow_dont_know',
            ],
            [
                'survey_node_answerable.id',
                'survey_node_answerable.node_id',
                'survey_node_answerable.type_constraint',
                'survey_node_answerable.allow_multiple',
                'survey_node_answerable.allow_other',
                'survey_node_answerable.allow_dont_know',
            ]
        ),
        sa.Index(
            'only_one_answer_allowed',
            'survey_node_id', 'submission_id',
            unique=True,
            postgresql_where=sa.not_(allow_multiple),
        ),
    )

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('deleted', self.deleted),
            ('answer_number', self.answer_number),
            ('submission_id', self.submission_id),
            ('submission_time', self.submission_time),
            ('survey_id', self.survey_id),
            ('survey_node_id', self.survey_node_id),
            ('question_id', self.node_id),
            ('type_constraint', self.type_constraint),
            ('last_update_time', self.last_update_time),
            ('response', self.response),
        ))


class _AnswerMixin:
    id = util.pk()
    the_allow_other = sa.Column(sa.Boolean, nullable=False)
    the_allow_dont_know = sa.Column(sa.Boolean, nullable=False)

    other = sa.Column(pg.TEXT)
    dont_know = sa.Column(pg.TEXT)


def _answer_mixin_table_args():
    return (
        sa.ForeignKeyConstraint(
            ['id', 'the_allow_other', 'the_allow_dont_know'],
            ['answer.id', 'answer.allow_other', 'answer.allow_dont_know']
        ),
        sa.CheckConstraint(
            # "other" responses are allowed XOR other is null
            '''
            the_allow_other != (other IS NULL)
            '''
        ),
        sa.CheckConstraint(
            # "dont_know" responses are allowed XOR dont_know is null
            '''
            the_allow_dont_know != (dont_know IS NULL)
            '''
        ),
        sa.CheckConstraint(
            '''
            (CASE WHEN (main_answer IS NOT NULL) AND
                       (other       IS     NULL) AND
                       (dont_know   IS     NULL)
                THEN 1 ELSE 0 END) +
            (CASE WHEN (main_answer IS     NULL) AND
                       (other       IS NOT NULL) AND
                       (dont_know   IS     NULL)
                THEN 1 ELSE 0 END) +
            (CASE WHEN (main_answer IS     NULL) AND
                       (other       IS     NULL) AND
                       (dont_know   IS NOT NULL)
                THEN 1 ELSE 0 END) =
            1
            '''
        ),
    )


class TextAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_text'
    main_answer = sa.Column(pg.TEXT)
    answer = synonym('main_answer')
    __mapper_args__ = {'polymorphic_identity': 'text'}
    __table_args__ = _answer_mixin_table_args()


class PhotoAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_photo'
    main_answer = sa.Column(pg.UUID, util.fk('photo.id'))
    answer = synonym('main_answer')
    photo = relationship('Photo')
    __mapper_args__ = {'polymorphic_identity': 'photo'}
    __table_args__ = _answer_mixin_table_args()

    def _asdict(self) -> OrderedDict:
        result = super()._asdict()
        result['photo'] = self.photo
        return result


# class LObject(UserDefinedType):
#     def get_col_spec(self):
#         return "lo"


class Photo(Base):
    __tablename__ = 'photo'

    id = util.pk()
    image = sa.Column(pg.BYTEA, nullable=False)
    # image = sa.Column(LObject)

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('deleted', self.deleted),
            ('image', self.image),
        ))


# sa.event.listen(
#     Photo.__table__,
#     'after_create',
#     sa.DDL(
#         'CREATE TRIGGER t_image BEFORE UPDATE OR DELETE ON photo'
#         ' FOR EACH ROW EXECUTE PROCEDURE lo_manage(image)'
#     ),
# )


class IntegerAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_integer'
    main_answer = sa.Column(sa.Integer)
    answer = synonym('main_answer')
    __mapper_args__ = {'polymorphic_identity': 'integer'}
    __table_args__ = _answer_mixin_table_args()


class DecimalAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_decimal'
    main_answer = sa.Column(pg.NUMERIC)
    answer = synonym('main_answer')
    __mapper_args__ = {'polymorphic_identity': 'decimal'}
    __table_args__ = _answer_mixin_table_args()


class DateAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_date'
    main_answer = sa.Column(sa.Date)
    answer = synonym('main_answer')
    __mapper_args__ = {'polymorphic_identity': 'date'}
    __table_args__ = _answer_mixin_table_args()


class TimeAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_time'
    main_answer = sa.Column(sa.Time(timezone=True))
    answer = synonym('main_answer')
    __mapper_args__ = {'polymorphic_identity': 'time'}
    __table_args__ = _answer_mixin_table_args()


class TimestampAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_timestamp'
    main_answer = sa.Column(pg.TIMESTAMP(timezone=True))
    answer = synonym('main_answer')
    __mapper_args__ = {'polymorphic_identity': 'timestamp'}
    __table_args__ = _answer_mixin_table_args()


class LocationAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_location'
    main_answer = sa.Column(Geometry('POINT', 4326))
    answer = synonym('main_answer')
    __mapper_args__ = {'polymorphic_identity': 'location'}
    __table_args__ = _answer_mixin_table_args()


class FacilityAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_facility'
    main_answer = sa.Column(Geometry('POINT', 4326))
    facility_id = sa.Column(pg.TEXT)
    facility_name = sa.Column(pg.TEXT)
    facility_sector = sa.Column(pg.TEXT)

    @hybrid_property
    def answer(self) -> OrderedDict:
        return OrderedDict((
            ('facility_location', self.main_answer),
            ('facility_id', self.facility_id),
            ('facility_name', self.facility_name),
            ('facility_sector', self.facility_sector),
        ))

    __mapper_args__ = {'polymorphic_identity': 'facility'}
    __table_args__ = _answer_mixin_table_args() + (
        sa.CheckConstraint(
            '''
            (CASE WHEN (main_answer     IS     NULL) AND
                       (facility_id     IS     NULL) AND
                       (facility_name   IS     NULL) AND
                       (facility_sector IS     NULL)
                THEN 1 ELSE 0 END) +
            (CASE WHEN (main_answer     IS NOT NULL) AND
                       (facility_id     IS NOT NULL) AND
                       (facility_name   IS NOT NULL) AND
                       (facility_sector IS NOT NULL)
                THEN 1 ELSE 0 END) =
            1
            '''
        ),
    )


class MultipleChoiceAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_multiple_choice'
    id = util.pk()
    the_allow_other = sa.Column(sa.Boolean, nullable=False)
    the_allow_dont_know = sa.Column(sa.Boolean, nullable=False)
    main_answer = sa.Column(pg.UUID)
    choice = relationship('Choice')
    answer = synonym('choice')
    the_survey_node_id = sa.Column(pg.UUID, nullable=False)
    the_question_id = sa.Column(pg.UUID, nullable=False)
    the_submission_id = sa.Column(pg.UUID, nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'multiple_choice'}
    __table_args__ = _answer_mixin_table_args()[1:] + (
        sa.ForeignKeyConstraint(
            [
                'id',
                'the_allow_other',
                'the_allow_dont_know',
                'the_survey_node_id',
                'the_question_id',
                'the_submission_id',
            ],
            [
                'answer.id',
                'answer.allow_other',
                'answer.allow_dont_know',
                'answer.survey_node_id',
                'answer.question_id',
                'answer.submission_id',
            ]
        ),
        sa.ForeignKeyConstraint(
            ['main_answer', 'the_question_id'],
            ['choice.id', 'choice.question_id']
        ),
        sa.UniqueConstraint(
            'the_survey_node_id', 'main_answer', 'the_submission_id',
            name='cannot_pick_the_same_choice_twice',
        ),
    )


ANSWER_TYPES = {
    'text': TextAnswer,
    'photo': PhotoAnswer,
    'integer': IntegerAnswer,
    'decimal': DecimalAnswer,
    'date': DateAnswer,
    'time': TimeAnswer,
    'timestamp': TimestampAnswer,
    'location': LocationAnswer,
    'facility': FacilityAnswer,
    'multiple_choice': MultipleChoiceAnswer,
}


def construct_answer(*, type_constraint: str, **kwargs) -> Answer:
    try:
        return ANSWER_TYPES[type_constraint](**kwargs)
    except KeyError:
        raise NoSuchNodeTypeError(type_constraint)
