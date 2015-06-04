"""Survey directed acyclic graph (dag) models."""

from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship

from dokomoforms.models import util, Base


class SurveyNode(Base):
    __tablename__ = 'survey_node'

    id = util.pk()
    survey_id = sa.Column(pg.UUID, util.fk('survey.id'))
    node_id = sa.Column(pg.UUID, util.fk('node.id'), nullable=False)
    node = relationship('Node')
    required = sa.Column(sa.Boolean, nullable=False, server_default='False')
    allow_dont_know = sa.Column(
        sa.Boolean, nullable=False, server_default='False'
    )
    logic = sa.Column(pg.json.JSON, nullable=False, server_default='{}')
    bucket = sa.Column(pg.TEXT, nullable=False, server_default='')
    parent_branch_id = sa.Column(pg.UUID, util.fk('survey_node.id'))
    nodes = relationship('SurveyNode')

    __table_args__ = (
        sa.CheckConstraint(
            '(survey_id IS NOT NULL) OR (parent_branch_id IS NOT NULL)',
            name='either_root_or_branch'
        ),
    )

    def _asdict(self) -> OrderedDict:
        result = self.node._asdict()
        result['logic'].update(self.logic)
        result['required'] = self.required
        result['allow_dont_know'] = self.required
        result['bucket'] = self.bucket
        result['nodes'] = self.nodes
        return result


class Survey(Base):
    """
    A survey is a collection of pointers to SurveyNodes.
    """
    __tablename__ = 'survey'

    id = util.pk()
    title = sa.Column(
        pg.TEXT,
        sa.CheckConstraint("title != ''", name='non_empty_survey_title'),
        nullable=False,
    )

    # TODO: expand upon this
    version = sa.Column(sa.Integer, nullable=False, server_default='1')
    # ODOT

    creator_id = sa.Column(
        pg.UUID, util.fk('survey_creator.id'), nullable=False
    )
    survey_metadata = sa.Column(
        pg.json.JSON, nullable=False, server_default='{}'
    )
    created_on = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_update_time = util.last_update_time()
    nodes = relationship('SurveyNode')

    __table_args__ = (
        sa.UniqueConstraint(
            'title', 'creator_id', name='unique_survey_name_per_user'
        ),
    )

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('title', self.title),
            ('version', self.version),
            ('creator', self.creator.name),
            ('metadata', self.survey_metadata),
            ('created_on', self.created_on),
            ('last_update_time', self.last_update_time),
            ('nodes', self.nodes),
        ))
