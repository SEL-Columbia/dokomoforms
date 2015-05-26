"""Question models."""

from collections import OrderedDict

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

    def _asdict(self) -> OrderedDict:
        contents = [
            ('id', self.id),
            ('title', self.title),
            ('hint', self.hint),
        ]
        if self.type_constraint == 'multiple_choice':
            contents.append(
                ('choices', [ch.choice_text for ch in self.choices])
            )
        contents.extend([
            ('allow_multiple', self.allow_multiple),
            ('type_constraint', self.type_constraint),
            ('logic', self.logic),
            ('last_update_time', self.last_update_time),
        ])
        return OrderedDict(contents)


class Choice(Base):
    """Models a choice for a type_constraint == multiple_choice question."""
    __tablename__ = 'choice'

    id = util.pk()
    choice_text = sa.Column(sa.String, nullable=False)
    choice_number = sa.Column(sa.Integer, nullable=False)
    question_id = sa.Column(
        pg.UUID, util.fk('question.id'), nullable=False
    )
    last_update_time = util.last_update_time()

    question = relationship(
        'Question',
        primaryjoin=(
            "and_("
            "    Question.id == Choice.question_id,"
            "    Question.type_constraint == 'multiple_choice',"
            ")"
        ),
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
