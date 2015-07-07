"""A Node is either a note or a question and is independent of a Survey."""

from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.declarative import declared_attr

from dokomoforms.models import util, Base
from dokomoforms.exc import NoSuchNodeTypeError


node_type_enum = sa.Enum(
    'text', 'photo', 'integer', 'decimal', 'date', 'time', 'timestamp',
    'location', 'facility', 'multiple_choice', 'note',
    name='type_constraint_name',
    inherit_schema=True,
    metadata=Base.metadata,
)


class Node(Base):

    """A node is a Note or Question independent of any Survey.

    A node is its own entity. A node can be a dokomoforms.models.survey.Note or
    a dokomoforms.models.survey.Question.

    You can use this class for querying, e.g.
        session.query(Node).filter_by(title='Some Title')

    To create the specific kind of Node you want, use
    dokomoforms.models.survey.node.construct_node.
    """

    __tablename__ = 'node'

    id = util.pk()
    languages = util.languages_column('languages')
    title = util.json_column('title')
    type_constraint = sa.Column(node_type_enum, nullable=False)
    logic = util.json_column('logic', default='{}')
    last_update_time = util.last_update_time()

    __mapper_args__ = {'polymorphic_on': type_constraint}
    __table_args__ = (
        sa.UniqueConstraint('id', 'type_constraint'),
        sa.UniqueConstraint('id', 'languages', 'type_constraint'),
        util.languages_constraint('title', 'languages'),
    )


class Note(Node):

    """Notes provide information interspersed with survey questions."""

    __tablename__ = 'note'

    id = util.pk()
    the_type_constraint = sa.Column(node_type_enum, nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'note'}
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id', 'the_type_constraint'], ['node.id', 'node.type_constraint']
        ),
    )

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('deleted', self.deleted),
            ('languages', self.languages),
            ('title', self.title),
            ('type_constraint', self.type_constraint),
            ('logic', self.logic),
            ('last_update_time', self.last_update_time),
        ))


class Question(Node):

    """A Question has a response type associated with it.

    A Question has a type constraint associated with it (integer, date,
    text...). Only a dokomoforms.models.survey.MultipleChoiceQuestion has a
    list of dokomoforms.models.survey.Choice instances.
    """

    __tablename__ = 'question'

    id = util.pk()
    the_languages = sa.Column(
        pg.ARRAY(pg.TEXT, as_tuple=True), nullable=False
    )
    the_type_constraint = sa.Column(node_type_enum, nullable=False)
    hint = util.json_column('hint', default='{"English": ""}')
    allow_multiple = sa.Column(
        sa.Boolean, nullable=False, server_default='false'
    )
    allow_other = sa.Column(
        sa.Boolean, nullable=False, server_default='false'
    )

    __table_args__ = (
        sa.UniqueConstraint(
            'id', 'the_languages', 'allow_multiple', 'allow_other'
        ),
        sa.CheckConstraint(
            "(the_type_constraint = 'multiple_choice') OR (NOT allow_other)"
        ),
        sa.ForeignKeyConstraint(
            ['id', 'the_languages', 'the_type_constraint'],
            ['node.id', 'node.languages', 'node.type_constraint']
        ),
        util.languages_constraint('hint', 'the_languages'),
    )

    def _default_asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('deleted', self.deleted),
            ('languages', self.languages),
            ('title', self.title),
            ('hint', self.hint),
            ('allow_multiple', self.allow_multiple),
            ('allow_other', self.allow_multiple),
            ('type_constraint', self.type_constraint),
            ('logic', self.logic),
            ('last_update_time', self.last_update_time),
        ))


class _QuestionMixin:
    @declared_attr
    def id(cls):
        return util.pk('node.id', 'question.id')

    def _asdict(self) -> OrderedDict:
        return super()._default_asdict()


class TextQuestion(_QuestionMixin, Question):

    """A text question."""

    __tablename__ = 'question_text'
    __mapper_args__ = {'polymorphic_identity': 'text'}


class PhotoQuestion(_QuestionMixin, Question):

    """A photo question."""

    __tablename__ = 'question_photo'
    __mapper_args__ = {'polymorphic_identity': 'photo'}


class IntegerQuestion(_QuestionMixin, Question):

    """A integer question."""

    __tablename__ = 'question_integer'
    __mapper_args__ = {'polymorphic_identity': 'integer'}


class DecimalQuestion(_QuestionMixin, Question):

    """A decimal question."""

    __tablename__ = 'question_decimal'
    __mapper_args__ = {'polymorphic_identity': 'decimal'}


class DateQuestion(_QuestionMixin, Question):

    """A date question."""

    __tablename__ = 'question_date'
    __mapper_args__ = {'polymorphic_identity': 'date'}


class TimeQuestion(_QuestionMixin, Question):

    """A time (with time zone) question."""

    __tablename__ = 'question_time'
    __mapper_args__ = {'polymorphic_identity': 'time'}


class TimestampQuestion(_QuestionMixin, Question):

    """A timestamp (with time zone) question."""

    __tablename__ = 'question_timestamp'
    __mapper_args__ = {'polymorphic_identity': 'timestamp'}


class LocationQuestion(_QuestionMixin, Question):

    """A location question."""

    __tablename__ = 'question_location'
    __mapper_args__ = {'polymorphic_identity': 'location'}


class FacilityQuestion(_QuestionMixin, Question):

    """A facility question."""

    __tablename__ = 'question_facility'
    __mapper_args__ = {'polymorphic_identity': 'facility'}


class MultipleChoiceQuestion(_QuestionMixin, Question):

    """A multiple_choice question."""

    __tablename__ = 'question_multiple_choice'

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
            ('title', OrderedDict(sorted(self.title.items()))),
            ('hint', self.hint),
            (
                'choices',
                [OrderedDict((
                    ('choice_id', choice.id),
                    (
                        'choice_text',
                        OrderedDict(sorted(choice.choice_text.items()))
                    ),
                )) for choice in self.choices]
            ),
            ('allow_multiple', self.allow_multiple),
            ('allow_other', self.allow_other),
            ('type_constraint', self.type_constraint),
            ('logic', self.logic),
            ('last_update_time', self.last_update_time),
        ))


class Choice(Base):

    """A choice for a MultipleChoiceQuestion.

    Models a choice for a dokomoforms.models.survey.MultipleChoiceQuestion.
    """

    __tablename__ = 'choice'

    id = util.pk()
    choice_text = util.json_column('choice_text')
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
        sa.UniqueConstraint('id', 'question_id'),
    )

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('deleted', self.deleted),
            ('choice_text', OrderedDict(sorted(self.choice_text.items()))),
            ('choice_number', self.choice_number),
            (
                'question',
                OrderedDict((
                    ('question_id', self.question_id),
                    (
                        'question_title',
                        OrderedDict(sorted(self.question.title.items()))
                    ),
                ))
            ),
            ('last_update_time', self.last_update_time),
        ))


NODE_TYPES = {
    'text': TextQuestion,
    'photo': PhotoQuestion,
    'integer': IntegerQuestion,
    'decimal': DecimalQuestion,
    'date': DateQuestion,
    'time': TimeQuestion,
    'timestamp': TimestampQuestion,
    'location': LocationQuestion,
    'facility': FacilityQuestion,
    'multiple_choice': MultipleChoiceQuestion,
    'note': Note,
}


def construct_node(*, type_constraint: str, **kwargs) -> Node:
    """Return a subclass of dokomoforms.models.node.Node.

    The subclass is determined by the type_constraint parameter. This utility
    function makes it easy to create an instance of a Node or Question
    subclass based on external input.

    See http://stackoverflow.com/q/30518484/1475412

    :param type_constraint: the type constraint of the node. Must be one of the
                            keys of
                            dokomoforms.models.survey.NODE_TYPES
    :param kwargs: the keyword arguments to pass to the constructor
    :returns: an instance of one of the Node subtypes
    :raises: dokomoforms.exc.NoSuchNodeTypeError
    """
    try:
        create_node = NODE_TYPES[type_constraint]
    except KeyError:
        raise NoSuchNodeTypeError(type_constraint)

    return create_node(**kwargs)
