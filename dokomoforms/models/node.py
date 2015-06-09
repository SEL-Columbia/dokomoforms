"""A Node is either a note or a question and is independent of a Survey."""

from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list

from dokomoforms.models import util, Base
from dokomoforms.exc import NoSuchNodeTypeError


node_type_enum = sa.Enum(
    'text', 'photo', 'integer', 'decimal', 'date', 'time', 'location',
    'facility', 'multiple_choice', 'note',
    name='type_constraint_name',
    inherit_schema=True,
    metadata=Base.metadata,
)


class Node(Base):
    """
    A node is its own entity. A node can be a dokomoforms.models.survey.Note or
    a dokomoforms.models.survey.Question.

    You can use this class for querying, e.g.
        session.query(Node).filter_by(title='Some Title')

    To create the specific kind of Node you want, use
    dokomoforms.models.survey.node.construct_node.
    """
    __tablename__ = 'node'

    id = util.pk()
    title = util.translatable_json_column()
    type_constraint = sa.Column(node_type_enum, nullable=False)
    logic = sa.Column(pg.json.JSONB, nullable=False, server_default='{}')
    last_update_time = util.last_update_time()

    __mapper_args__ = {'polymorphic_on': type_constraint}
    __table_args__ = (
        sa.UniqueConstraint('id', 'type_constraint'),
    )


class Note(Node):
    """Notes provide information interspersed with survey questions."""
    __tablename__ = 'note'

    id = util.pk('node.id')

    __mapper_args__ = {'polymorphic_identity': 'note'}

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('deleted', self.deleted),
            ('title', self.title),
            ('type_constraint', self.type_constraint),
            ('logic', self.logic),
            ('last_update_time', self.last_update_time),
        ))


class Question(Node):
    """
    A question has a type constraint associated with it (integer, date,
    text...). Only a dokomoforms.models.survey.MultipleChoiceQuestion has a
    list of dokomoforms.models.survey.Choice instances.
    """
    __tablename__ = 'question'

    id = util.pk('node.id')
    hint = util.translatable_json_column()
    allow_multiple = sa.Column(
        sa.Boolean, nullable=False, server_default='false'
    )
    allow_other = sa.Column(
        sa.Boolean, nullable=False, server_default='false'
    )

    def _default_asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('title', self.title),
            ('hint', self.hint),
            ('allow_multiple', self.allow_multiple),
            ('allow_other', self.allow_multiple),
            ('type_constraint', self.type_constraint),
            ('logic', self.logic),
            ('last_update_time', self.last_update_time),
        ))


class TextQuestion(Question):
    __tablename__ = 'question_text'

    id = util.pk('node.id', 'question.id')

    __mapper_args__ = {'polymorphic_identity': 'text'}

    def _asdict(self) -> OrderedDict:
        return super()._default_asdict()


class PhotoQuestion(Question):
    __tablename__ = 'question_photo'

    id = util.pk('node.id', 'question.id')

    __mapper_args__ = {'polymorphic_identity': 'photo'}

    def _asdict(self) -> OrderedDict:
        return super()._default_asdict()


class IntegerQuestion(Question):
    __tablename__ = 'question_integer'

    id = util.pk('node.id', 'question.id')

    __mapper_args__ = {'polymorphic_identity': 'integer'}

    def _asdict(self) -> OrderedDict:
        return super()._default_asdict()


class DecimalQuestion(Question):
    __tablename__ = 'question_decimal'

    id = util.pk('node.id', 'question.id')

    __mapper_args__ = {'polymorphic_identity': 'decimal'}

    def _asdict(self) -> OrderedDict:
        return super()._default_asdict()


class DateQuestion(Question):
    __tablename__ = 'question_date'

    id = util.pk('node.id', 'question.id')

    __mapper_args__ = {'polymorphic_identity': 'date'}

    def _asdict(self) -> OrderedDict:
        return super()._default_asdict()


class TimeQuestion(Question):
    __tablename__ = 'question_time'

    id = util.pk('node.id', 'question.id')

    __mapper_args__ = {'polymorphic_identity': 'time'}

    def _asdict(self) -> OrderedDict:
        return super()._default_asdict()


class LocationQuestion(Question):
    __tablename__ = 'question_location'

    id = util.pk('node.id', 'question.id')

    __mapper_args__ = {'polymorphic_identity': 'location'}

    def _asdict(self) -> OrderedDict:
        return super()._default_asdict()


class FacilityQuestion(Question):
    __tablename__ = 'question_facility'

    id = util.pk('node.id', 'question.id')

    __mapper_args__ = {'polymorphic_identity': 'facility'}

    def _asdict(self) -> OrderedDict:
        return super()._default_asdict()


class MultipleChoiceQuestion(Question):
    __tablename__ = 'question_multiple_choice'

    id = util.pk('node.id', 'question.id')
    choices = relationship(
        'Choice',
        order_by='Choice.choice_number',
        collection_class=ordering_list('choice_number'),
        backref='question',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    __mapper_args__ = {'polymorphic_identity': 'multiple_choice'}

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('deleted', self.deleted),
            ('title', self.title),
            ('hint', self.hint),
            ('choices', [choice.choice_text for choice in self.choices]),
            ('allow_multiple', self.allow_multiple),
            ('allow_other', self.allow_other),
            ('type_constraint', self.type_constraint),
            ('logic', self.logic),
            ('last_update_time', self.last_update_time),
        ))


class Choice(Base):
    """
    Models a choice for a dokomoforms.models.survey.MultipleChoiceQuestion.
    """
    __tablename__ = 'choice'

    id = util.pk()
    choice_text = util.translatable_json_column()
    choice_number = sa.Column(sa.Integer, nullable=False)
    question_id = sa.Column(
        pg.UUID, util.fk('question_multiple_choice.id'), nullable=False
    )
    last_update_time = util.last_update_time()

    __table_args__ = (
        sa.UniqueConstraint(
            'question_id', 'choice_number', name='unique_choice_number'
        ),
        sa.UniqueConstraint(
            'question_id', 'choice_text', name='unique_choice_text'
        ),
    )

    __table_args__ = (
        sa.UniqueConstraint('id', 'question_id'),
    )

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('deleted', self.deleted),
            ('choice_text', self.choice_text),
            ('choice_number', self.choice_number),
            ('question', self.question.title),
            ('last_update_time', self.last_update_time),
        ))


NODE_TYPES = {
    'text': TextQuestion,
    'photo': PhotoQuestion,
    'integer': IntegerQuestion,
    'decimal': DecimalQuestion,
    'date': DateQuestion,
    'time': TimeQuestion,
    'location': LocationQuestion,
    'facility': FacilityQuestion,
    'multiple_choice': MultipleChoiceQuestion,
    'note': Note,
}


def construct_node(*, type_constraint: str, **kwargs) -> Node:
    """
    Returns a subclass of dokomoforms.models.survey.Node determined by
    the type_constraint parameter. This utility function makes it easy to
    create an instance of a Node or Question subclass based on external
    input.

    See http://stackoverflow.com/q/30518484/1475412

    :param type_constraint: the type constraint of the node. Must be one of the
                            keys of
                            dokomoforms.models.survey.NODE_TYPES
    :param kwargs: the keyword arguments to pass to the constructor
    :returns: an instance of one of the Node subtypes
    :raises: dokomoforms.exc.NoSuchNodeTypeError
    """
    try:
        return NODE_TYPES[type_constraint](**kwargs)
    except KeyError:
        raise NoSuchNodeTypeError(type_constraint)
