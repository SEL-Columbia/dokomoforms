"""Question models."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship, backref

from dokomoforms.models import util, Base


class Question(Base):
    """Models a question."""
    __tablename__ = 'question'

    id = util.pk()
    title = sa.Column(
        sa.String,
        sa.CheckConstraint("title != ''", name='non_empty_title'),
        nullable=False,
    )
    hint = sa.Column(sa.String, nullable=False, server_default='')
    allow_multiple = sa.Column(
        sa.Boolean, nullable=False, server_default='False'
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
        'polymorphic_identity': 'question',
        'polymorphic_on': type_constraint,
    }


class MultipleChoiceQuestion(Question):
    """
    Multiple choice questions have choices
    (dokomoforms.models.question.Choice)
    """
    __tablename__ = 'question_multiple_choice'

    id = util.pk('question.id')

    __mapper_args__ = {'polymorphic_identity': 'multiple_choice'}


class Choice(Base):
    """Models a choice for a multiple_choice question."""
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
