"""Survey models."""

from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list

from dokomoforms.models import util, Base


class Survey(Base):
    __tablename__ = 'survey'

    id = util.pk()
    title = sa.Column(
        pg.TEXT,
        sa.CheckConstraint("title != ''", name='non_empty_survey_title'),
        nullable=False,
    )
    default_language = sa.Column(
        pg.TEXT,
        sa.CheckConstraint(
            "default_language != ''", name='non_empty_default_language'
        ),
        nullable=False,
        server_default='English',
    )
    translations = sa.Column(
        pg.json.JSONB, nullable=False, server_default='{}'
    )
    # TODO: expand upon this
    version = sa.Column(sa.Integer, nullable=False, server_default='1')
    # ODOT
    creator_id = sa.Column(
        pg.UUID, util.fk('survey_creator.id'), nullable=False
    )
    survey_metadata = sa.Column(
        pg.json.JSONB, nullable=False, server_default='{}'
    )
    created_on = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    nodes = relationship(
        'SurveyNode',
        order_by='SurveyNode.node_number',
        collection_class=ordering_list('node_number'),
        cascade='all, delete-orphan',
        passive_updates=True,
        passive_deletes=True,
    )
    last_update_time = util.last_update_time()

    __table_args__ = (
        sa.UniqueConstraint(
            'title', 'creator_id', name='unique_survey_title_per_user'
        ),
    )

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('deleted', self.deleted),
            ('title', self.title),
            ('default_language', self.default_language),
            ('translations', self.translations),
            ('version', self.version),
            ('creator', self.creator.name),
            ('metadata', self.survey_metadata),
            ('created_on', self.created_on),
            ('last_update_time', self.last_update_time),
            ('nodes', self.nodes),
        ))


_sub_survey_nodes = sa.Table(
    'sub_survey_nodes',
    Base.metadata,
    sa.Column('sub_survey_id', pg.UUID, sa.ForeignKey('sub_survey.id')),
    sa.Column('survey_node_id', pg.UUID, sa.ForeignKey('survey_node.id')),
)


class SubSurvey(Base):
    __tablename__ = 'sub_survey'

    id = util.pk()
    sub_survey_number = sa.Column(sa.Integer, nullable=False)
    bucket = sa.Column(pg.TEXT, nullable=False)
    repeatable = sa.Column(sa.Boolean, nullable=False, server_default='false')
    nodes = relationship(
        'SurveyNode',
        secondary=_sub_survey_nodes,
        order_by='SurveyNode.node_number',
        collection_class=ordering_list('node_number'),
        cascade='all, delete-orphan',
        passive_updates=True,
        passive_deletes=True,
        single_parent=True,
    )

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('deleted', self.deleted),
            ('bucket', self.bucket),
            ('repeatable', self.repeatable),
            ('nodes', self.nodes),
        ))


_node_sub_surveys = sa.Table(
    'node_sub_surveys',
    Base.metadata,
    sa.Column('survey_node_id', pg.UUID, sa.ForeignKey('survey_node.id')),
    sa.Column('sub_survey_id', pg.UUID, sa.ForeignKey('sub_survey.id')),
)


class SurveyNode(Base):
    __tablename__ = 'survey_node'

    id = util.pk()
    node_number = sa.Column(sa.Integer, nullable=False)
    node_id = sa.Column(pg.UUID, util.fk('node.id'), nullable=False)
    node = relationship('Node')
    root_survey_id = sa.Column(pg.UUID, util.fk('survey.id'))
    nodes = relationship(
        'SubSurvey',
        secondary=_node_sub_surveys,
        order_by='SubSurvey.sub_survey_number',
        collection_class=ordering_list('sub_survey_number'),
        cascade='all, delete-orphan',
        passive_updates=True,
        passive_deletes=True,
        single_parent=True,
    )
    required = sa.Column(sa.Boolean, nullable=False, server_default='false')
    allow_dont_know = sa.Column(
        sa.Boolean, nullable=False, server_default='false'
    )
    logic = sa.Column(pg.json.JSONB, nullable=False, server_default='{}')

    def _asdict(self) -> OrderedDict:
        result = self.node._asdict()
        result['logic'].update(self.logic)
        result['node_id'] = result.pop('id')
        result['deleted'] = self.deleted
        result['required'] = self.required
        result['allow_dont_know'] = self.required
        if self.nodes:
            result['nodes'] = self.nodes
        return result
