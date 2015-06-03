"""Survey directed acyclic graph (dag) models."""

from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship

from dokomoforms.models import util, Base


class SurveyToNodeAssociation(Base):
    """
    This association object connects Survey instances to SurveyNode instances
    in a many-to-many relationship.
    """
    __tablename__ = 'survey_to_survey_node_association'

    survey_id = util.pk('survey.id')
    survey_node_id = util.pk('survey_node.id')
    node = relationship('SurveyNode')

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('survey_id', self.survey_id),
            ('survey_node', self.node),
        ))


class Survey(Base):
    """
    A survey is a collection of pointers to nodes.
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
    nodes = relationship('SurveyToNodeAssociation')

    __table_args__ = (
        sa.UniqueConstraint(
            'title', 'creator_id', name='unique survey name per user'
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
