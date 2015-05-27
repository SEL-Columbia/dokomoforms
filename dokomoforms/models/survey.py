"""Survey models."""

from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship, backref

from dokomoforms.models import util, Base


class SurveyNode(Base):
    """
    A survey node is its own entity. A survey is a collection of pointers to
    nodes. A survey node can be a dokomoforms.models.survey.Note or a
    dokomoforms.models.survey.Question.

    You can use this class for querying, e.g.
        session.query(SurveyNode).filter_by(title='Some Title')
    """
    __tablename__ = 'survey_node'

    id = util.pk()
    title = sa.Column(
        sa.String,
        sa.CheckConstraint("title != ''", name='non_empty_title'),
        nullable=False,
    )
    type_constraint = sa.Column(
        sa.Enum(
            'text', 'integer', 'decimal', 'date', 'time', 'location',
            'facility', 'multiple_choice', 'note',
            name='type_constraint_name',
            inherit_schema=True,
        ),
        nullable=False,
    )
    logic = sa.Column(pg.json.JSON, nullable=False, server_default='{}')
    last_update_time = util.last_update_time()

    __mapper_args__ = {
        'polymorphic_on': type_constraint,
        # 'with_polymorphic': '*',
    }


class Note(SurveyNode):
    """Notes provide information interspersed with survey questions."""
    __tablename__ = 'note'

    id = util.pk('survey_node.id')

    __mapper_args__ = {'polymorphic_identity': 'note'}

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('title', self.title),
            ('type_constraint', self.type_constraint),
            ('logic', self.logic),
            ('last_update_time', self.last_update_time),
        ))


class Question(SurveyNode):
    """
    A question has a type constraint associated with it (integer, date,
    text...). Only a dokomoforms.models.survey.MultipleChoiceQuestion has a
    list of dokomoforms.models.survey.Choice instances.

    Do not instantiate this class. Instead, instantiate one of the menagerie
    of models which inherit from Question.
    """
    __tablename__ = 'question'
    id = util.pk('survey_node.id')

    hint = sa.Column(sa.String, nullable=False, server_default='')
    allow_multiple = sa.Column(
        sa.Boolean, nullable=False, server_default='False'
    )

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('title', self.title),
            ('hint', self.hint),
            ('allow_multiple', self.allow_multiple),
            ('type_constraint', self.type_constraint),
            ('logic', self.logic),
            ('last_update_time', self.last_update_time),
        ))


class TextQuestion(Question):
    __tablename__ = 'question_text'

    id = util.pk('survey_node.id', 'question.id')

    __mapper_args__ = {'polymorphic_identity': 'text'}


class MultipleChoiceQuestion(Question):
    __tablename__ = 'question_multiple_choice'

    id = util.pk('survey_node.id', 'question.id')

    __mapper_args__ = {'polymorphic_identity': 'multiple_choice'}

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('title', self.title),
            ('hint', self.hint),
            ('choices', [choice.choice_text for choice in self.choices]),
            ('allow_multiple', self.allow_multiple),
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
    choice_text = sa.Column(sa.String, nullable=False)
    choice_number = sa.Column(sa.Integer, nullable=False)
    question_id = sa.Column(
        pg.UUID, util.fk('question_multiple_choice.id'), nullable=False
    )
    last_update_time = util.last_update_time()

    question = relationship(
        'MultipleChoiceQuestion',
        backref=backref('choices', order_by=choice_number),
    )

    __table_args__ = (
        sa.UniqueConstraint(
            'question_id', 'choice_number', name='unique_choice_number'
        ),
        sa.UniqueConstraint(
            'question_id', 'choice_text', name='unique_choice_text'
        ),
    )

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('choice_text', self.choice_text),
            ('choice_number', self.choice_number),
            ('question', self.question.title),
            ('last_update_time', self.last_update_time),
        ))
