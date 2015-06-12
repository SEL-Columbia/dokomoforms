"""Survey models."""

from collections import OrderedDict

import datetime
import dateutil.parser

import sqlalchemy as sa
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list

from dokomoforms.models import util, Base, node_type_enum
from dokomoforms.exc import NoSuchBucketTypeError


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
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=current_timestamp(),
    )
    nodes = relationship(
        'SurveyNode',
        order_by='SurveyNode.node_number',
        collection_class=ordering_list('node_number'),
        cascade='all, delete-orphan',
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
    sa.Column('sub_survey_id', sa.Integer, sa.ForeignKey('sub_survey.id')),
    sa.Column('survey_node_id', pg.UUID, sa.ForeignKey('survey_node.id')),
)


class SubSurvey(Base):
    __tablename__ = 'sub_survey'

    id = sa.Column(sa.Integer, primary_key=True)
    sub_survey_number = sa.Column(sa.Integer, nullable=False)
    parent_survey_node_id = sa.Column(pg.UUID, nullable=False)
    parent_node_id = sa.Column(pg.UUID, nullable=False)
    parent_type_constraint = sa.Column(node_type_enum, nullable=False)
    buckets = relationship(
        'Bucket',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    repeatable = sa.Column(sa.Boolean, nullable=False, server_default='false')
    nodes = relationship(
        'SurveyNode',
        secondary=_sub_survey_nodes,
        order_by='SurveyNode.node_number',
        collection_class=ordering_list('node_number'),
        cascade='all, delete-orphan',
        passive_deletes=True,
        single_parent=True,
    )

    __table_args__ = (
        sa.UniqueConstraint(
            'id', 'parent_type_constraint', 'parent_survey_node_id',
            'parent_node_id'
        ),
        sa.UniqueConstraint('parent_survey_node_id', 'parent_node_id'),
        sa.ForeignKeyConstraint(
            ['parent_survey_node_id', 'parent_type_constraint',
                'parent_node_id'],
            ['survey_node.id', 'survey_node.type_constraint',
                'survey_node.node_id'],
            onupdate='CASCADE', ondelete='CASCADE'
        ),
    )

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('deleted', self.deleted),
            ('buckets', [bucket.bucket for bucket in self.buckets]),
            ('repeatable', self.repeatable),
            ('nodes', self.nodes),
        ))


class Bucket(Base):
    __tablename__ = 'bucket'

    id = util.pk()
    sub_survey_id = sa.Column(sa.Integer, nullable=False)
    sub_survey_parent_type_constraint = sa.Column(
        node_type_enum, nullable=False
    )
    sub_survey_parent_survey_node_id = sa.Column(pg.UUID, nullable=False)
    sub_survey_parent_node_id = sa.Column(pg.UUID, nullable=False)
    bucket_type = sa.Column(
        sa.Enum(
            'integer', 'decimal', 'date', 'time', 'timestamp',
            'multiple_choice',
            name='bucket_type_name',
            inherit_schema=True,
        ),
        nullable=False,
    )
    last_update_time = util.last_update_time()

    __mapper_args__ = {'polymorphic_on': bucket_type}
    __table_args__ = (
        sa.CheckConstraint(
            'bucket_type::TEXT = sub_survey_parent_type_constraint::TEXT'
        ),
        sa.ForeignKeyConstraint(
            [
                'sub_survey_id',
                'sub_survey_parent_type_constraint',
                'sub_survey_parent_survey_node_id',
                'sub_survey_parent_node_id'
            ],
            [
                'sub_survey.id',
                'sub_survey.parent_type_constraint',
                'sub_survey.parent_survey_node_id',
                'sub_survey.parent_node_id'
            ],
            onupdate='CASCADE', ondelete='CASCADE'
        ),
        sa.UniqueConstraint('id', 'sub_survey_id'),
        sa.UniqueConstraint(
            'id', 'sub_survey_id', 'sub_survey_parent_survey_node_id',
            'sub_survey_parent_node_id'
        ),
    )

    def _default_asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('bucket_type', self.bucket_type),
            ('bucket', self.bucket),
        ))


def _bucket_range_constraints() -> tuple:
    return (
        pg.ExcludeConstraint(('the_sub_survey_id', '='), ('bucket', '&&')),
        sa.CheckConstraint('NOT isempty(bucket)'),
        sa.ForeignKeyConstraint(
            ['id', 'the_sub_survey_id'], ['bucket.id', 'bucket.sub_survey_id'],
            onupdate='CASCADE', ondelete='CASCADE'
        ),
    )


class IntegerBucket(Bucket):
    __tablename__ = 'bucket_integer'

    id = util.pk()
    the_sub_survey_id = sa.Column(sa.Integer, nullable=False)
    bucket = sa.Column(pg.INT4RANGE, nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'integer'}
    __table_args__ = _bucket_range_constraints()

    def _asdict(self) -> OrderedDict:
        return super()._default_asdict()


class DecimalBucket(Bucket):
    __tablename__ = 'bucket_decimal'

    id = util.pk()
    the_sub_survey_id = sa.Column(sa.Integer, nullable=False)
    bucket = sa.Column(pg.NUMRANGE, nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'decimal'}
    __table_args__ = _bucket_range_constraints()

    def _asdict(self) -> OrderedDict:
        return super()._default_asdict()


class DateBucket(Bucket):
    __tablename__ = 'bucket_date'

    id = util.pk()
    the_sub_survey_id = sa.Column(sa.Integer, nullable=False)
    bucket = sa.Column(pg.DATERANGE, nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'date'}
    __table_args__ = _bucket_range_constraints()

    def _asdict(self) -> OrderedDict:
        return super()._default_asdict()


class TimeBucket(Bucket):
    __tablename__ = 'bucket_time'

    id = util.pk()
    the_sub_survey_id = sa.Column(sa.Integer, nullable=False)
    bucket = sa.Column(pg.TSTZRANGE, nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'time'}
    __table_args__ = (
        _bucket_range_constraints() +
        (
            sa.CheckConstraint("date(lower(bucket)) = '1970-01-01'"),
            sa.CheckConstraint("date(upper(bucket)) = '1970-01-01'"),
        )
    )

    def _asdict(self) -> OrderedDict:
        return super()._default_asdict()


class TimeStampBucket(Bucket):
    __tablename__ = 'bucket_timestamp'

    id = util.pk()
    the_sub_survey_id = sa.Column(sa.Integer, nullable=False)
    bucket = sa.Column(pg.TSTZRANGE, nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'timestamp'}
    __table_args__ = _bucket_range_constraints()

    def _asdict(self) -> OrderedDict:
        return super()._default_asdict()


class MultipleChoiceBucket(Bucket):
    __tablename__ = 'bucket_multiple_choice'

    id = util.pk()
    the_sub_survey_id = sa.Column(sa.Integer, nullable=False)
    choice_id = sa.Column(pg.UUID, nullable=False)
    bucket = relationship('Choice')
    parent_survey_node_id = sa.Column(pg.UUID, nullable=False)
    parent_node_id = sa.Column(pg.UUID, nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'multiple_choice'}
    __table_args__ = (
        sa.UniqueConstraint('choice_id', 'the_sub_survey_id'),
        sa.ForeignKeyConstraint(
            ['choice_id', 'parent_node_id'],
            ['choice.id', 'choice.question_id'],
            onupdate='CASCADE', ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            [
                'id',
                'the_sub_survey_id',
                'parent_survey_node_id',
                'parent_node_id'
            ],
            [
                'bucket.id',
                'bucket.sub_survey_id',
                'bucket.sub_survey_parent_survey_node_id',
                'bucket.sub_survey_parent_node_id'
            ],
            onupdate='CASCADE', ondelete='CASCADE'
        ),
    )

    def _asdict(self) -> OrderedDict:
        return super()._default_asdict()


BUCKET_TYPES = {
    'integer': IntegerBucket,
    'decimal': DecimalBucket,
    'date': DateBucket,
    'time': TimeBucket,
    'timestamp': TimeStampBucket,
    'multiple_choice': MultipleChoiceBucket,
}


def _set_date_to_unix_epoch(time: str) -> datetime.datetime:
    return datetime.datetime.combine(
        datetime.datetime(1970, 1, 1), dateutil.parser.parse(time).time()
    )


def construct_bucket(*, bucket_type: str, **kwargs) -> Bucket:
    try:
        create_bucket = BUCKET_TYPES[bucket_type]
    except KeyError:
        raise NoSuchBucketTypeError(bucket_type)

    if bucket_type == 'time' and 'bucket' in kwargs:
        bucket_str = kwargs['bucket'].strip()

        open_bracket = bucket_str[0]
        bucket_str_contents = bucket_str[1:-1]
        close_bracket = bucket_str[-1]

        lower, upper = bucket_str_contents.split(',')

        kwargs['bucket'] = (
            open_bracket + _set_date_to_unix_epoch(lower).isoformat() + ',' +
            _set_date_to_unix_epoch(upper).isoformat() + close_bracket
        )

    return create_bucket(**kwargs)


class SurveyNode(Base):
    __tablename__ = 'survey_node'

    id = util.pk()
    node_number = sa.Column(sa.Integer, nullable=False)
    node_id = sa.Column(pg.UUID, nullable=False)
    type_constraint = sa.Column(node_type_enum, nullable=False)
    node = relationship('Node')
    root_survey_id = sa.Column(pg.UUID, util.fk('survey.id'))
    nodes = relationship(
        'SubSurvey',
        order_by='SubSurvey.sub_survey_number',
        collection_class=ordering_list('sub_survey_number'),
        cascade='all, delete-orphan',
        passive_deletes=True,
        single_parent=True,
    )
    required = sa.Column(sa.Boolean, nullable=False, server_default='false')
    allow_dont_know = sa.Column(
        sa.Boolean, nullable=False, server_default='false'
    )
    logic = sa.Column(pg.json.JSONB, nullable=False, server_default='{}')

    __table_args__ = (
        sa.UniqueConstraint('id', 'node_id', 'type_constraint'),
        sa.ForeignKeyConstraint(
            ['node_id', 'type_constraint'],
            ['node.id', 'node.type_constraint'],
            onupdate='CASCADE', ondelete='CASCADE'
        ),
    )

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
