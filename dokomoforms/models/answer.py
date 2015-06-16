"""Answer models."""

import abc
from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship, synonym
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
# from sqlalchemy.sql.type_api import UserDefinedType

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
    node_id = sa.Column(pg.UUID, nullable=False)
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
        sa.UniqueConstraint('id', 'node_id'),
        sa.ForeignKeyConstraint(
            ['submission_id', 'submission_time', 'survey_id'],
            ['submission.id', 'submission.submission_time',
                'submission.survey_id']
        ),
        sa.ForeignKeyConstraint(
            ['survey_node_id', 'node_id', 'type_constraint'],
            ['survey_node.id', 'survey_node.node_id',
                'survey_node.type_constraint']
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
            ('node_id', self.node_id),
            ('type_constraint', self.type_constraint),
            ('last_update_time', self.last_update_time),
            ('response', self.response),
        ))


class _AnswerMixin:
    @declared_attr
    def id(cls):
        return util.pk('answer.id')

    @declared_attr
    def answer(cls):
        return synonym('main_answer')

    other = sa.Column(pg.TEXT)
    dont_know = sa.Column(pg.TEXT)

    @declared_attr
    def __table_args__(cls):
        return (
            sa.CheckConstraint(
                '''
                (CASE WHEN main_answer IS NOT NULL THEN 1 ELSE 0 END) +
                (CASE WHEN other       IS NOT NULL THEN 1 ELSE 0 END) +
                (CASE WHEN dont_know   IS NOT NULL THEN 1 ELSE 0 END) =
                1
                '''
            ),
        )


class TextAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_text'
    main_answer = sa.Column(pg.TEXT)
    __mapper_args__ = {'polymorphic_identity': 'text'}


class PhotoAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_photo'
    main_answer = sa.Column(pg.UUID, util.fk('photo.id'))
    photo = relationship('Photo')
    __mapper_args__ = {'polymorphic_identity': 'photo'}

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
    __mapper_args__ = {'polymorphic_identity': 'integer'}


class DecimalAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_decimal'
    main_answer = sa.Column(pg.NUMERIC)
    __mapper_args__ = {'polymorphic_identity': 'decimal'}


class DateAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_date'
    main_answer = sa.Column(sa.Date)
    __mapper_args__ = {'polymorphic_identity': 'date'}


class TimeAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_time'
    main_answer = sa.Column(sa.Time(timezone=True))
    __mapper_args__ = {'polymorphic_identity': 'date'}


class TimestampAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_timestamp'
    main_answer = sa.Column(pg.TIMESTAMP(timezone=True))
    __mapper_args__ = {'polymorphic_identity': 'timestamp'}


class LocationAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_location'
    main_answer = sa.Column(sa.Integer)  # Geometry
    __mapper_args__ = {'polymorphic_identity': 'location'}


class FacilityAnswer(_AnswerMixin, Answer):
    __tablename__ = 'answer_facility'
    main_answer = sa.Column(sa.Integer)  # Geometry
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

    @declared_attr
    def __table_args__(cls):
        return _AnswerMixin.__table_args__ + (
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
    main_answer = sa.Column(pg.UUID)
    choice = relationship('Choice')
    answer = synonym('choice')
    the_node_id = sa.Column(pg.UUID, nullable=False)
    __mapper_args__ = {'polymorphic_identity': 'multiple_choice'}

    @declared_attr
    def __table_args__(cls):
        return _AnswerMixin.__table_args__ + (
            sa.ForeignKeyConstraint(
                ['id', 'the_node_id'], ['answer.id', 'answer.node_id']
            ),
            sa.ForeignKeyConstraint(
                ['main_answer', 'the_node_id'],
                ['choice.id', 'choice.question_id']
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
