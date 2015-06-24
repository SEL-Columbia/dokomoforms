"""Survey models."""

import abc
from collections import OrderedDict

import datetime
import dateutil.parser

import sqlalchemy as sa
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.sql.elements import quoted_name
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.orderinglist import ordering_list

from dokomoforms.models import util, Base, node_type_enum
from dokomoforms.exc import NoSuchBucketTypeError


survey_type_enum = sa.Enum(
    'false', 'true',
    name='enumerator_only_enum',
    inherit_schema=True,
)


class Survey(Base):

    """A Survey has a list of SurveyNodes.

    Use an EnumeratorOnlySurvey to restrict submissions to enumerators.
    """

    __tablename__ = 'survey'

    id = util.pk()
    title = util.json_column('title')
    default_language = sa.Column(
        pg.TEXT,
        sa.CheckConstraint(
            "default_language != ''", name='non_empty_default_language'
        ),
        nullable=False,
        server_default='English',
    )
    enumerator_only = sa.Column(survey_type_enum, nullable=False)
    submissions = relationship(
        'Submission',
        order_by='Submission.save_time',
        backref='survey',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    # TODO: expand upon this
    version = sa.Column(sa.Integer, nullable=False, server_default='1')
    # ODOT
    creator_id = sa.Column(
        pg.UUID, util.fk('survey_creator.id'), nullable=False
    )

    # This is survey_metadata rather than just metadata because all models
    # have a metadata attribute which is important for SQLAlchemy.
    survey_metadata = util.json_column('survey_metadata', default='{}')

    created_on = sa.Column(
        pg.TIMESTAMP(timezone=True),
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

    __mapper_args__ = {
        'polymorphic_on': enumerator_only,
        'polymorphic_identity': 'false',
    }
    __table_args__ = (
        sa.UniqueConstraint(
            'title', 'creator_id', name='unique_survey_title_per_user'
        ),
        sa.UniqueConstraint('id', 'enumerator_only'),
        sa.CheckConstraint(
            "title ? default_language",
            name='title_in_default_langauge_exists'
        ),
        sa.CheckConstraint(
            "(title->>default_language) != ''",
            name='title_in_default_langauge_non_empty'
        ),
    )

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('deleted', self.deleted),
            ('title', self.title),
            ('default_language', self.default_language),
            ('enumerator_only', self.enumerator_only),
            ('version', self.version),
            ('creator_id', self.creator_id),
            ('creator_name', self.creator.name),
            ('metadata', self.survey_metadata),
            ('created_on', self.created_on),
            ('last_update_time', self.last_update_time),
            ('nodes', self.nodes),
        ))


_enumerator_table = sa.Table(
    'enumerator',
    Base.metadata,
    sa.Column(
        'enumerator_only_survey_id',
        pg.UUID,
        util.fk('survey_enumerator_only.id'),
        nullable=False,
    ),
    sa.Column('user_id', pg.UUID, util.fk('auth_user.id'), nullable=False),
    sa.UniqueConstraint('enumerator_only_survey_id', 'user_id'),
)


class EnumeratorOnlySurvey(Survey):

    """Only enumerators (designated Users) can submit to this."""

    __tablename__ = 'survey_enumerator_only'

    id = util.pk('survey')
    enumerators = relationship(
        'User',
        secondary=_enumerator_table,
        backref='allowed_surveys',
        passive_deletes=True,
    )

    __mapper_args__ = {'polymorphic_identity': 'true'}


_sub_survey_nodes = sa.Table(
    'sub_survey_nodes',
    Base.metadata,
    sa.Column(
        'sub_survey_id',
        pg.UUID,
        sa.ForeignKey('sub_survey.id'),
        nullable=False,
    ),
    sa.Column('survey_node_id', pg.UUID, nullable=False),
    sa.Column('survey_node_number', sa.Integer, nullable=False),
    sa.ForeignKeyConstraint(
        ['survey_node_id', 'survey_node_number'],
        ['survey_node.id', 'survey_node.node_number']
    ),
)


class SubSurvey(Base):

    """A SubSurvey behaves like a Survey but belongs to a SurveyNode.

    The way to arrive at a certain SubSurvey is encoded in its buckets.
    """

    __tablename__ = 'sub_survey'

    id = util.pk()
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
            [
                'parent_survey_node_id',
                'parent_type_constraint',
                'parent_node_id',
            ],
            [
                'survey_node_answerable.id',
                'survey_node_answerable.type_constraint',
                'survey_node_answerable.node_id'
            ],
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

    """A Bucket determines how to arrive at a SubSurvey.

    A Bucket can be a range or a Choice.
    """

    __tablename__ = 'bucket'

    id = util.pk()
    sub_survey_id = sa.Column(pg.UUID, nullable=False)
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

    @property
    @abc.abstractmethod
    def bucket(self):
        """The bucket is a range or Choice.

        Buckets for a given SubSurvey cannot overlap.
        """
        pass

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

    def _asdict(self) -> OrderedDict:
        return OrderedDict((
            ('id', self.id),
            ('bucket_type', self.bucket_type),
            ('bucket', self.bucket),
        ))


class _RangeBucketMixin:
    id = util.pk()
    the_sub_survey_id = sa.Column(pg.UUID, nullable=False)

    @declared_attr
    def __table_args__(cls):
        return (
            pg.ExcludeConstraint(
                (
                    # Workaround for
                    # https://bitbucket.org/zzzeek/sqlalchemy/issue/3454
                    # For SQLAlchemy 1.0.6, replace with actual cast()
                    sa.Column(quoted_name(
                        'CAST("the_sub_survey_id" AS TEXT)', quote=False
                    )),
                    '='
                ),
                ('bucket', '&&')
            ),
            sa.CheckConstraint('NOT isempty(bucket)'),
            sa.ForeignKeyConstraint(
                ['id', 'the_sub_survey_id'],
                ['bucket.id', 'bucket.sub_survey_id'],
                onupdate='CASCADE', ondelete='CASCADE'
            ),
        )


class IntegerBucket(_RangeBucketMixin, Bucket):

    """INT4RANGE bucket."""

    __tablename__ = 'bucket_integer'
    bucket = sa.Column(pg.INT4RANGE, nullable=False)
    __mapper_args__ = {'polymorphic_identity': 'integer'}


class DecimalBucket(_RangeBucketMixin, Bucket):

    """NUMRANGE bucket."""

    __tablename__ = 'bucket_decimal'
    bucket = sa.Column(pg.NUMRANGE, nullable=False)
    __mapper_args__ = {'polymorphic_identity': 'decimal'}


class DateBucket(_RangeBucketMixin, Bucket):

    """DATERANGE bucket."""

    __tablename__ = 'bucket_date'
    bucket = sa.Column(pg.DATERANGE, nullable=False)
    __mapper_args__ = {'polymorphic_identity': 'date'}


class TimeBucket(_RangeBucketMixin, Bucket):

    """TSTZRANGE bucket which ignores the date."""

    __tablename__ = 'bucket_time'
    bucket = sa.Column(pg.TSTZRANGE, nullable=False)
    __mapper_args__ = {'polymorphic_identity': 'time'}


class TimestampBucket(_RangeBucketMixin, Bucket):

    """TSTZRANGE bucket."""

    __tablename__ = 'bucket_timestamp'
    bucket = sa.Column(pg.TSTZRANGE, nullable=False)
    __mapper_args__ = {'polymorphic_identity': 'timestamp'}


class MultipleChoiceBucket(Bucket):

    """Choice id bucket."""

    __tablename__ = 'bucket_multiple_choice'

    id = util.pk()
    the_sub_survey_id = sa.Column(pg.UUID, nullable=False)
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


BUCKET_TYPES = {
    'integer': IntegerBucket,
    'decimal': DecimalBucket,
    'date': DateBucket,
    'time': TimeBucket,
    'timestamp': TimestampBucket,
    'multiple_choice': MultipleChoiceBucket,
}


TZINFOS = dict()


def _set_tzinfos():
    global TZINFOS
    if not TZINFOS:
        from dokomoforms.models import create_engine
        engine = create_engine(echo=False)
        connection = engine.connect()
        tzinfos = connection.execute(
            'SELECT abbrev, utc_offset FROM pg_timezone_abbrevs'
        )
        connection.close()
        TZINFOS = {
            abbrev: int(offset.total_seconds()) for abbrev, offset in tzinfos
        }
        del engine


def _time_at_unix_epoch_date(time: str, upper=False) -> datetime.datetime:
    the_date = datetime.datetime(1970, 1, 1)
    if upper and time.strip() == '':
        the_date = datetime.datetime(1970, 1, 2)
    return datetime.datetime.combine(
        the_date, dateutil.parser.parse(time, tzinfos=TZINFOS).timetz()
    )


def _set_time_bucket_dates(bucket: str) -> str:
    bucket_str = bucket.strip()

    open_bracket = bucket_str[0]
    bucket_str_contents = bucket_str[1:-1]
    close_bracket = bucket_str[-1]

    lower, upper = bucket_str_contents.split(',')

    return (
        open_bracket +
        _time_at_unix_epoch_date(lower).isoformat() + ',' +
        _time_at_unix_epoch_date(upper, upper=True).isoformat() +
        close_bracket
    )


def construct_bucket(*, bucket_type: str, **kwargs) -> Bucket:
    """Return a subclass of dokomoforms.models.survey.Bucket.

    The subclass is determined by the bucket_type parameter. This utility
    function makes it easy to create an instance of a Bucket subclass based
    on external input.

    See http://stackoverflow.com/q/30518484/1475412

    :param bucket_type: the type of the bucket. Must be one of the keys of
                        dokomoforms.models.survey.BUCKET_TYPES
    :param kwargs: the keyword arguments to pass to the constructor
    :returns: an instance of one of the Bucket subtypes
    :raises: dokomoforms.exc.NoSuchBucketTypeError
    """
    try:
        create_bucket = BUCKET_TYPES[bucket_type]
    except KeyError:
        raise NoSuchBucketTypeError(bucket_type)

    if bucket_type == 'time' and 'bucket' in kwargs:
        kwargs['bucket'] = _set_time_bucket_dates(kwargs['bucket'])

    return create_bucket(**kwargs)


class SurveyNode(Base):

    """A SurveyNode contains a Node and adds survey-specific metadata."""

    __tablename__ = 'survey_node'

    id = util.pk()
    node_number = sa.Column(sa.Integer, nullable=False)

    survey_node_answerable = sa.Column(
        sa.Enum(
            'non_answerable', 'answerable',
            name='answerable_enum', inherit_schema=True
        ),
        nullable=False,
    )

    @property
    @abc.abstractmethod
    def node_id(self):
        """The id of the Node."""

    @property
    @abc.abstractmethod
    def node(self):
        """The Node instance."""

    @property
    @abc.abstractmethod
    def type_constraint(self):
        """The type_constraint of the Node."""

    root_survey_id = sa.Column(pg.UUID, util.fk('survey.id'))
    logic = util.json_column('logic', default='{}')
    last_update_time = util.last_update_time()

    __mapper_args__ = {'polymorphic_on': survey_node_answerable}
    __table_args__ = (
        sa.UniqueConstraint('id', 'node_number'),
        sa.UniqueConstraint('root_survey_id', 'node_number'),
    )

    def _asdict(self) -> OrderedDict:
        result = self.node._asdict()
        result['logic'].update(self.logic)
        result['node_id'] = result.pop('id')
        result['id'] = self.id
        result['deleted'] = self.deleted
        result['last_update_time'] = self.last_update_time
        return result


class NonAnswerableSurveyNode(SurveyNode):

    """Contains a Node which is not answerablei (e.g., a Note)."""

    __tablename__ = 'survey_node_non_answerable'

    id = util.pk('survey_node.id')
    node_id = sa.Column(pg.UUID, nullable=False)
    type_constraint = sa.Column(node_type_enum, nullable=False)
    node = relationship('Note')

    __mapper_args__ = {'polymorphic_identity': 'non_answerable'}
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['node_id', 'type_constraint'],
            ['note.id', 'note.the_type_constraint']
        ),
    )


class AnswerableSurveyNode(SurveyNode):

    """Contains a Node which is answerable (.e.g, a Question)."""

    __tablename__ = 'survey_node_answerable'

    id = util.pk('survey_node.id')
    node_id = sa.Column(pg.UUID, nullable=False)
    type_constraint = sa.Column(node_type_enum, nullable=False)
    allow_multiple = sa.Column(sa.Boolean, nullable=False)
    allow_other = sa.Column(sa.Boolean, nullable=False)
    node = relationship('Question')
    sub_surveys = relationship(
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
    answers = relationship('Answer', order_by='Answer.submission_time')

    __mapper_args__ = {'polymorphic_identity': 'answerable'}
    __table_args__ = (
        sa.UniqueConstraint('id', 'type_constraint', 'node_id'),
        sa.UniqueConstraint(
            'id', 'node_id', 'type_constraint', 'allow_multiple',
            'allow_other', 'allow_dont_know'
        ),
        sa.ForeignKeyConstraint(
            [
                'node_id',
                'type_constraint',
                'allow_multiple',
                'allow_other',
            ],
            [
                'question.id',
                'question.the_type_constraint',
                'question.allow_multiple',
                'question.allow_other',
            ]
        ),
    )

    def _asdict(self) -> OrderedDict:
        result = super()._asdict()
        result['required'] = self.required
        result['allow_dont_know'] = self.allow_dont_know
        if self.sub_surveys:
            result['sub_surveys'] = self.sub_surveys
        return result
