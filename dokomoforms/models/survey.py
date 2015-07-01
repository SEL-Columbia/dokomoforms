"""Survey models."""

import abc
from collections import OrderedDict

import datetime
import dateutil.parser

import sqlalchemy as sa
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.orderinglist import ordering_list

from dokomoforms.models import util, Base, node_type_enum
from dokomoforms.exc import NoSuchBucketTypeError


survey_type_enum = sa.Enum(
    'public', 'enumerator_only',
    name='enumerator_only_enum',
    inherit_schema=True,
)


_administrator_table = sa.Table(
    'administrator',
    Base.metadata,
    sa.Column(
        'survey_id',
        pg.UUID,
        util.fk('survey.id'),
        nullable=False,
    ),
    sa.Column('user_id', pg.UUID, util.fk('auth_user.id'), nullable=False),
    sa.UniqueConstraint('survey_id', 'user_id'),
)


class Survey(Base):

    """A Survey has a list of SurveyNodes.

    Use an EnumeratorOnlySurvey to restrict submissions to enumerators.
    """

    __tablename__ = 'survey'

    id = util.pk()
    languages = util.languages_column('languages')
    title = util.json_column('title')
    default_language = sa.Column(
        pg.TEXT,
        sa.CheckConstraint(
            "default_language != ''", name='non_empty_default_language'
        ),
        nullable=False,
        server_default='English',
    )
    survey_type = sa.Column(survey_type_enum, nullable=False)
    administrators = relationship(
        'User',
        secondary=_administrator_table,
        backref='admin_surveys',
        passive_deletes=True,
    )
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
        'polymorphic_on': survey_type,
        'polymorphic_identity': 'public',
    }
    __table_args__ = (
        sa.UniqueConstraint(
            'title', 'creator_id', name='unique_survey_title_per_user'
        ),
        sa.UniqueConstraint('id', 'survey_type'),
        sa.UniqueConstraint('id', 'languages'),
        util.languages_constraint('title', 'languages'),
        sa.CheckConstraint(
            "languages @> ARRAY[default_language]",
            name='default_language_in_languages_exists'
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
            ('title', OrderedDict(sorted(self.title.items()))),
            ('default_language', self.default_language),
            ('survey_type', self.survey_type),
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

    __mapper_args__ = {'polymorphic_identity': 'enumerator_only'}


class SubSurvey(Base):

    """A SubSurvey behaves like a Survey but belongs to a SurveyNode.

    The way to arrive at a certain SubSurvey is encoded in its buckets.
    """

    __tablename__ = 'sub_survey'

    id = util.pk()
    sub_survey_number = sa.Column(sa.Integer, nullable=False)
    root_survey_languages = sa.Column(
        pg.ARRAY(pg.TEXT, as_tuple=False), nullable=False
    )
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
        order_by='SurveyNode.node_number',
        collection_class=ordering_list('node_number'),
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    __table_args__ = (
        sa.UniqueConstraint('id', 'root_survey_languages'),
        sa.UniqueConstraint(
            'id', 'parent_type_constraint', 'parent_survey_node_id',
            'parent_node_id'
        ),
        sa.UniqueConstraint('parent_survey_node_id', 'parent_node_id'),
        sa.ForeignKeyConstraint(
            [
                'parent_survey_node_id',
                'root_survey_languages',
                'parent_type_constraint',
                'parent_node_id',
            ],
            [
                'survey_node_answerable.id',
                'survey_node_answerable.the_root_survey_languages',
                'survey_node_answerable.the_type_constraint',
                'survey_node_answerable.the_node_id',
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

    @property  # pragma: no cover
    @abc.abstractmethod
    def bucket(self):
        """The bucket is a range or Choice.

        Buckets for a given SubSurvey cannot overlap.
        """

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
                'sub_survey_parent_node_id',
            ],
            [
                'sub_survey.id',
                'sub_survey.parent_type_constraint',
                'sub_survey.parent_survey_node_id',
                'sub_survey.parent_node_id',
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
                (sa.cast(cls.the_sub_survey_id, pg.TEXT), '='),
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
                'parent_node_id',
            ],
            [
                'bucket.id',
                'bucket.sub_survey_id',
                'bucket.sub_survey_parent_survey_node_id',
                'bucket.sub_survey_parent_node_id',
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


def _time_at_unix_epoch_date(time: str, upper=False) -> datetime.datetime:
    the_date = datetime.datetime(1970, 1, 1)
    if upper and time.strip() == '':
        the_date = datetime.datetime(1970, 1, 2)
    return datetime.datetime.combine(
        the_date, dateutil.parser.parse(time).timetz()
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

    node_id = sa.Column(pg.UUID, nullable=False)
    node_languages = sa.Column(
        pg.ARRAY(pg.TEXT, as_tuple=True), nullable=False
    )
    type_constraint = sa.Column(node_type_enum, nullable=False)
    the_node = relationship('Node')

    @property  # pragma: no cover
    @abc.abstractmethod
    def node(self):
        """The Node instance."""

    root_survey_id = sa.Column(pg.UUID)
    root_survey_languages = sa.Column(
        pg.ARRAY(pg.TEXT, as_tuple=True), nullable=False
    )
    sub_survey_id = sa.Column(pg.UUID)
    logic = util.json_column('logic', default='{}')
    last_update_time = util.last_update_time()

    __mapper_args__ = {'polymorphic_on': survey_node_answerable}
    __table_args__ = (
        sa.UniqueConstraint('id', 'node_number'),
        sa.UniqueConstraint('id', 'node_id', 'type_constraint'),
        sa.UniqueConstraint(
            'id', 'root_survey_languages', 'node_id', 'type_constraint'
        ),
        sa.UniqueConstraint('root_survey_id', 'node_number'),
        sa.CheckConstraint(
            '(root_survey_id IS NULL) != (sub_survey_id IS NULL)'
        ),
        sa.CheckConstraint(
            'root_survey_languages @> node_languages',
            name='all_survey_languages_present_in_node_languages'
        ),
        sa.ForeignKeyConstraint(
            ['root_survey_id', 'root_survey_languages'],
            ['survey.id', 'survey.languages']
        ),
        sa.ForeignKeyConstraint(
            ['sub_survey_id', 'root_survey_languages'],
            ['sub_survey.id', 'sub_survey.root_survey_languages']
        ),
        sa.ForeignKeyConstraint(
            ['node_id', 'node_languages', 'type_constraint'],
            ['node.id', 'node.languages', 'node.type_constraint']
        ),
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

    """Contains a Node which is not answerable (e.g., a Note)."""

    __tablename__ = 'survey_node_non_answerable'

    id = util.pk()
    the_node_id = sa.Column(pg.UUID, util.fk('note.id'), nullable=False)
    the_type_constraint = sa.Column(node_type_enum, nullable=False)
    node = relationship('Note')

    __mapper_args__ = {'polymorphic_identity': 'non_answerable'}
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['id', 'the_node_id', 'the_type_constraint'],
            ['survey_node.id', 'survey_node.node_id',
                'survey_node.type_constraint']
        ),
    )


class AnswerableSurveyNode(SurveyNode):

    """Contains a Node which is answerable (.e.g, a Question)."""

    __tablename__ = 'survey_node_answerable'

    id = util.pk()
    the_root_survey_languages = sa.Column(
        pg.ARRAY(pg.TEXT, as_tuple=True), nullable=False
    )
    the_node_id = sa.Column(pg.UUID, nullable=False)
    the_node_languages = sa.Column(
        pg.ARRAY(pg.TEXT, as_tuple=True), nullable=False
    )
    the_type_constraint = sa.Column(node_type_enum, nullable=False)
    allow_multiple = sa.Column(sa.Boolean, nullable=False)
    allow_other = sa.Column(sa.Boolean, nullable=False)
    node = relationship('Question')
    sub_surveys = relationship(
        'SubSurvey',
        order_by='SubSurvey.sub_survey_number',
        collection_class=ordering_list('sub_survey_number'),
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    required = sa.Column(sa.Boolean, nullable=False, server_default='false')
    allow_dont_know = sa.Column(
        sa.Boolean, nullable=False, server_default='false'
    )
    answers = relationship('Answer', order_by='Answer.submission_time')

    __mapper_args__ = {'polymorphic_identity': 'answerable'}
    __table_args__ = (
        sa.UniqueConstraint(
            'id', 'the_root_survey_languages', 'the_type_constraint',
            'the_node_id'
        ),
        sa.UniqueConstraint(
            'id', 'the_node_id', 'the_type_constraint', 'allow_multiple',
            'allow_other', 'allow_dont_know'
        ),
        sa.ForeignKeyConstraint(
            [
                'id',
                'the_root_survey_languages',
                'the_node_id',
                'the_type_constraint',
            ],
            [
                'survey_node.id',
                'survey_node.root_survey_languages',
                'survey_node.node_id',
                'survey_node.type_constraint',
            ]
        ),
        sa.ForeignKeyConstraint(
            [
                'the_node_id',
                'the_node_languages',
                'allow_multiple',
                'allow_other',
            ],
            [
                'question.id',
                'question.the_languages',
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


def construct_survey_node(**kwargs) -> SurveyNode:
    """
    Returns a subclass of dokomoforms.models.survey.SurveyNode determined by
    the type_constraint parameter. This utility function makes it easy to
    create an instance of a SurveyNode subclass based on external
    input.

    See http://stackoverflow.com/q/30518484/1475412

    :param kwargs: the keyword arguments to pass to the constructor
    :returns: an instance of one of the Node subtypes
    """

    if 'node' in kwargs:
        type_constraint = kwargs['node'].type_constraint
        if 'the_node' not in kwargs:
            kwargs['the_node'] = kwargs['node']

    if 'type_constraint' in kwargs:
        type_constraint = kwargs['type_constraint']

    survey_node_constructor = (
        NonAnswerableSurveyNode if type_constraint
        is 'note' else AnswerableSurveyNode
    )

    return survey_node_constructor(**kwargs)
    # # it's unclear whether an id passed into kwargs should
    # # pertain to the survey_node or node? Since it's unlikely
    # # that an id will be passed except for testing cases,
    # # for now it's BOTH.
    # if 'id' in kwargs:
    #     survey_node = survey_node_constructor(
    #         id=kwargs['id'],
    #         the_node=node,
    #         node=node,
    #     )
    # else:
    #     survey_node = survey_node_constructor(
    #         the_node=node,
    #         node=node,
    #     )
    # return survey_node
