"""Set up database access."""
from sqlalchemy import create_engine, Table, Column, String, MetaData, \
    DateTime, ForeignKey, UniqueConstraint, Index, Integer, Boolean, \
    CheckConstraint, ForeignKeyConstraint, Numeric, Date, Time, event, DDL

from sqlalchemy.engine import Engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import Update, Delete, func, cast, not_
from sqlalchemy.sql.type_api import UserDefinedType

from settings import CONNECTION_STRING


engine = create_engine(CONNECTION_STRING, convert_unicode=True, pool_size=0,
                       max_overflow=-1)

metadata = MetaData()

auth_user_table = Table(
    'auth_user', metadata,
    Column('auth_user_id', postgresql.UUID, primary_key=True,
           server_default=func.uuid_generate_v4()),
    Column('email', String,
           unique=True,
           nullable=False),
    Column('token', String,
           server_default='',
           nullable=False),
    Column('expires_on', DateTime(timezone=True),
           nullable=False,
           server_default=func.now()),
    Column('auth_user_last_update_time', DateTime(timezone=True),
           nullable=False,
           server_default=func.now(),
           onupdate=func.utc_timestamp()),
)

event.listen(
    metadata, 'after_create',
    DDL('ALTER TABLE auth_user OWNER TO postgres')
)

survey_table = Table(
    'survey', metadata,
    Column('survey_id', postgresql.UUID, primary_key=True,
           server_default=func.uuid_generate_v4()),
    Column('survey_title', String,
           nullable=False),
    Column('auth_user_id', postgresql.UUID,
           ForeignKey('auth_user.auth_user_id',
                      onupdate='CASCADE',
                      ondelete='CASCADE'),
           nullable=False),
    Column('metadata', postgresql.json.JSON,
           nullable=False, server_default='{}'),
    Column('created_on', DateTime(timezone=True),
           nullable=False,
           server_default=func.now()),
    Column('survey_last_update_time', DateTime(timezone=True),
           nullable=False,
           server_default=func.now(),
           onupdate=func.utc_timestamp()),
    UniqueConstraint('survey_title', 'auth_user_id',
                     name='survey_title_survey_owner_key')
)

Index('survey_id_btree_tpo', cast(survey_table.c.survey_id, String),
      postgresql_ops={'survey_id': 'text_pattern_ops'})

event.listen(
    metadata, 'after_create',
    DDL('ALTER TABLE survey OWNER TO postgres')
)

type_constraint_table = Table(
    'type_constraint', metadata,
    Column('type_constraint_id', postgresql.UUID, primary_key=True,
           server_default=func.uuid_generate_v4()),
    Column('type_constraint_name', String,
           unique=True, nullable=False),
    Column('type_constraint_last_update_time', DateTime(timezone=True),
           nullable=False,
           server_default=func.now(),
           onupdate=func.utc_timestamp())
)

event.listen(
    metadata, 'after_create',
    DDL('ALTER TABLE type_constraint OWNER TO postgres')
)

submission_table = Table(
    'submission', metadata,
    Column('submission_id', postgresql.UUID, primary_key=True,
           server_default=func.uuid_generate_v4()),
    Column('submission_time', DateTime(timezone=True),
           nullable=False,
           server_default=func.now()),
    Column('submitter', String,
           nullable=False),
    Column('survey_id', postgresql.UUID,
           ForeignKey('survey.survey_id',
                      onupdate='CASCADE',
                      ondelete='CASCADE'),
           nullable=False),
    Column('field_update_time', DateTime(timezone=True),
           nullable=False,
           server_default=func.now()),
    Column('submission_last_update_time', DateTime(timezone=True),
           nullable=False,
           server_default=func.now(),
           onupdate=func.utc_timestamp())
)

event.listen(
    metadata, 'after_create',
    DDL('ALTER TABLE submission OWNER TO postgres')
)

question_table = Table(
    'question', metadata,
    Column('question_id', postgresql.UUID, primary_key=True,
           server_default=func.uuid_generate_v4()),
    Column('question_title', String,
           CheckConstraint("question_title != ''", name='non_empty_title'),
           nullable=False),
    Column('hint', String,
           nullable=False,
           server_default=''),
    Column('sequence_number', Integer,
           CheckConstraint('sequence_number >= 0',
                           name='nonnegative_sequence_number'),
           primary_key=True,
           nullable=False),
    Column('question_to_sequence_number', Integer,
           nullable=False),
    Column('allow_multiple', Boolean, primary_key=True,
           nullable=False,
           server_default='False'),
    Column('type_constraint_name', String,
           ForeignKey('type_constraint.type_constraint_name',
                      onupdate='CASCADE',
                      ondelete='CASCADE'),
           primary_key=True),
    Column('logic', postgresql.json.JSON,
           CheckConstraint(
               "((logic->>'required')) IS NOT NULL AND "
               "((logic->>'with_other')) IS NOT NULL",
               name='minimal_logic'),
           nullable=False,
           server_default='{"required": false, "with_other": false}'),
    Column('survey_id', postgresql.UUID,
           ForeignKey('survey.survey_id',
                      onupdate='CASCADE',
                      ondelete='CASCADE'),
           primary_key=True),
    Column('question_last_update_time', DateTime(timezone=True),
           nullable=False,
           server_default=func.now(),
           onupdate=func.utc_timestamp()),
    UniqueConstraint('survey_id', 'sequence_number',
                     name='question_survey_id_sequence_number_key')
)

event.listen(
    metadata, 'after_create',
    DDL('ALTER TABLE question OWNER TO postgres')
)

question_choice_table = Table(
    'question_choice', metadata,
    Column('question_choice_id', postgresql.UUID, primary_key=True,
           server_default=func.uuid_generate_v4()),
    Column('choice', String,
           nullable=False),
    Column('choice_number', Integer,
           nullable=False),
    Column('question_id', postgresql.UUID, primary_key=True),
    Column('type_constraint_name', String,
           CheckConstraint("type_constraint_name = 'multiple_choice'",
                           name='question_should_have_choices'),
           primary_key=True),
    Column('question_sequence_number', Integer, primary_key=True),
    Column('allow_multiple', Boolean, primary_key=True),
    Column('survey_id', postgresql.UUID, primary_key=True),
    Column('question_choice_last_update_time', DateTime(timezone=True),
           nullable=False,
           server_default=func.now(),
           onupdate=func.utc_timestamp()),
    ForeignKeyConstraint(
        ['question_id', 'type_constraint_name', 'question_sequence_number',
         'allow_multiple', 'survey_id'],
        ['question.question_id', 'question.type_constraint_name',
         'question.sequence_number', 'question.allow_multiple',
         'question.survey_id'],
        onupdate='CASCADE',
        ondelete='CASCADE'),
    UniqueConstraint('question_id', 'choice_number',
                     name='unique_choice_number'),
    UniqueConstraint('question_id', 'choice',
                     name='unique_choice_names')
)

event.listen(
    metadata, 'after_create',
    DDL('ALTER TABLE question_choice OWNER TO postgres')
)

question_branch_table = Table(
    'question_branch', metadata,
    Column('question_branch_id', postgresql.UUID, primary_key=True,
           server_default=func.uuid_generate_v4()),
    Column('question_choice_id', postgresql.UUID, nullable=False),
    Column('from_question_id', postgresql.UUID, nullable=False),
    Column('from_type_constraint', String,
           CheckConstraint("from_type_constraint = 'multiple_choice'",
                           name='question_could_have_choices'),
           nullable=False),
    Column('from_sequence_number', Integer, nullable=False),
    Column('from_allow_multiple', Boolean,
           CheckConstraint('NOT from_allow_multiple',
                           name='cannot_allow_multiple'),
           nullable=False),
    Column('from_survey_id', postgresql.UUID, nullable=False),
    Column('to_question_id', postgresql.UUID, nullable=False),
    Column('to_type_constraint', String, nullable=False),
    Column('to_sequence_number', Integer, nullable=False),
    Column('to_allow_multiple', Boolean, nullable=False),
    Column('to_survey_id', postgresql.UUID, nullable=False),
    Column('question_branch_last_update_time', DateTime(timezone=True),
           nullable=False,
           server_default=func.now(),
           onupdate=func.utc_timestamp()),
    ForeignKeyConstraint(
        ['question_choice_id', 'from_question_id', 'from_type_constraint',
         'from_sequence_number', 'from_allow_multiple', 'from_survey_id'],
        ['question_choice.question_choice_id', 'question_choice.question_id',
         'question_choice.type_constraint_name',
         'question_choice.question_sequence_number',
         'question_choice.allow_multiple', 'question_choice.survey_id'],
        onupdate='CASCADE',
        ondelete='CASCADE'),
    ForeignKeyConstraint(
        ['to_question_id', 'to_type_constraint', 'to_sequence_number',
         'to_allow_multiple', 'to_survey_id'],
        ['question.question_id', 'question.type_constraint_name',
         'question.sequence_number', 'question.allow_multiple',
         'question.survey_id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    ),
    UniqueConstraint('from_question_id', 'question_choice_id'),
    CheckConstraint('to_sequence_number > from_sequence_number',
                    name='cannot_point_backward'),
    CheckConstraint('from_survey_id = to_survey_id',
                    name='cannot_point_to_another_survey')
)

event.listen(
    metadata, 'after_create',
    DDL('ALTER TABLE question_branch OWNER TO postgres')
)


class Geometry(UserDefinedType):
    def get_col_spec(self):
        return "GEOMETRY"

        # def bind_expression(self, bindvalue):
        # return func.ST_GeomFromText(bindvalue, type_=self)
        #
        # def column_expression(self, colexpr):
        # return func.ST_AsText(colexpr, type_=self)


answer_table = Table(
    'answer', metadata,
    Column('answer_id', postgresql.UUID, primary_key=True,
           server_default=func.uuid_generate_v4()),
    Column('answer_text', String),
    Column('answer_integer', Integer),
    Column('answer_decimal', Numeric),
    Column('answer_date', Date),
    Column('answer_time', Time(timezone=True)),
    Column('answer_location', Geometry),
    Column('question_id', postgresql.UUID, nullable=False),
    Column('type_constraint_name', String,
           CheckConstraint("type_constraint_name != 'note'",
                           name='note_questions_cannot_be_answered'),
           nullable=False),
    Column('sequence_number', Integer, nullable=False),
    Column('allow_multiple', Boolean, nullable=False),
    Column('survey_id', postgresql.UUID, nullable=False),
    Column('submission_id', postgresql.UUID,
           ForeignKey('submission.submission_id',
                      onupdate='CASCADE',
                      ondelete='CASCADE'),
           nullable=False),
    Column('answer_last_update_time', DateTime(timezone=True),
           nullable=False,
           server_default=func.now(),
           onupdate=func.utc_timestamp()),
    ForeignKeyConstraint(
        ['question_id', 'type_constraint_name', 'sequence_number',
         'allow_multiple', 'survey_id'],
        ['question.question_id', 'question.type_constraint_name',
         'question.sequence_number', 'question.allow_multiple',
         'question.survey_id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    ),
    CheckConstraint(
        '''
        (CASE WHEN type_constraint_name in ('text', 'multiple_choice')
                                        AND   answer_text     IS NOT NULL
          THEN 1 ELSE 0 END) +
        (CASE WHEN type_constraint_name =   'integer'
                                        AND ((answer_integer  IS NULL) !=
                                             (answer_text     IS NULL))
          THEN 1 ELSE 0 END) +
        (CASE WHEN type_constraint_name =   'decimal'
                                        AND ((answer_decimal  IS NULL) !=
                                             (answer_text     IS NULL))
          THEN 1 ELSE 0 END) +
        (CASE WHEN type_constraint_name =   'date'
                                        AND ((answer_date     IS NULL) !=
                                             (answer_text     IS NULL))
          THEN 1 ELSE 0 END) +
        (CASE WHEN type_constraint_name =   'time'
                                        AND ((answer_time     IS NULL) !=
                                             (answer_text     IS NULL))
          THEN 1 ELSE 0 END) +
        (CASE WHEN type_constraint_name =   'location'
                                        AND ((answer_location IS NULL) !=
                                             (answer_text     IS NULL))
          THEN 1 ELSE 0 END) +
        (CASE WHEN type_constraint_name =   'facility'
                                        AND answer_location IS NOT NULL
                                        AND answer_text     IS NOT NULL
          THEN 1 ELSE 0 END)
        = 1
        '''
    )
)

Index('only_one_answer_allowed',
      answer_table.c.question_id, answer_table.c.submission_id,
      unique=True,
      postgresql_where=not_(answer_table.c.allow_multiple))

event.listen(
    metadata, 'after_create',
    DDL('ALTER TABLE answer OWNER TO postgres')
)

answer_choice_table = Table(
    'answer_choice', metadata,
    Column('answer_choice_id', postgresql.UUID, primary_key=True,
           server_default=func.uuid_generate_v4()),
    Column('question_choice_id', postgresql.UUID, nullable=False),
    Column('question_id', postgresql.UUID, nullable=False),
    Column('type_constraint_name', String,
           CheckConstraint("type_constraint_name = 'multiple_choice'",
                           name='multiple_choice_answer_type_matches'),
           nullable=False),
    Column('sequence_number', Integer, nullable=False),
    Column('allow_multiple', Boolean, nullable=False),
    Column('survey_id', postgresql.UUID, nullable=False),
    Column('submission_id', postgresql.UUID,
           ForeignKey('submission.submission_id',
                      onupdate='CASCADE',
                      ondelete='CASCADE'),
           nullable=False),
    Column('answer_choice_last_update_time', DateTime(timezone=True),
           nullable=False,
           server_default=func.now(),
           onupdate=func.utc_timestamp()),
    ForeignKeyConstraint(
        ['question_choice_id', 'question_id', 'type_constraint_name',
         'sequence_number', 'allow_multiple', 'survey_id'],
        ['question_choice.question_choice_id', 'question_choice.question_id',
         'question_choice.type_constraint_name',
         'question_choice.question_sequence_number',
         'question_choice.allow_multiple', 'question_choice.survey_id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    ),
    UniqueConstraint('question_choice_id', 'submission_id')
)

Index('only_one_choice_allowed',
      answer_choice_table.c.submission_id, answer_choice_table.c.question_id,
      unique=True,
      postgresql_where=not_(answer_choice_table.c.allow_multiple))

event.listen(
    metadata, 'after_create',
    DDL('ALTER TABLE answer_choice OWNER TO postgres')
)


def set_testing_engine(testing_engine: Engine):
    """
    Use this function to set an alternate testing engine (like SQLite):

    import db

    from sqlalchemy import create_engine

    db.set_engine(create_engine(CONNECTION_STRING, convert_unicode=True))

    :param testing_engine: A SQLAlchemy engine
    """
    global engine
    engine = testing_engine


_UPD_TYPE_ERR = '''Cannot specify the update values in both a dict and
keyword arguments.'''


def update_record(table: Table,
                  uuid_column_name: str,
                  uuid_value: str,
                  values_dict: dict=None,
                  **values) -> Update:
    """
    Update a record in the specified table identified by the given primary
    key name and value. You can give the values to update in either the
    values_dict parameter or as keyword arguments.

    Make sure you use a transaction!

    >>> update_record(survey_table, 'survey_id', survey_id, title='new_title')
    <sqlalchemy.sql.dml.Update object at 0x...>

    >>> update_record(survey_table, 'survey_id', survey_id,
    {'title':'new_title'})
    <sqlalchemy.sql.dml.Update object at 0x...>


    :param table: The SQLAlchemy table
    :param uuid_column_name: The UUID primary key column name
    :param uuid_value: The UUID specifying the record
    :param values_dict: The new values. If given, you cannot also give
                        keyword arguments.
    :param values: The new values. If given, you cannot also give the
                   values_dict parameter.
    :return: A SQLAlchemy Update object. Execute this!
    """

    # Check that this function was called with either the value_dict
    # parameter or kwargs
    if values_dict:
        if values:
            raise TypeError(_UPD_TYPE_ERR)
        values = values_dict
    elif not values:
        raise TypeError('No update values specified.')
    # An update bumps the record's last_update_time column
    values[table.name + '_last_update_time'] = 'now()'
    condition = get_column(table, uuid_column_name) == uuid_value
    return table.update().where(condition).values(values)


def delete_record(table: Table,
                  uuid_column_name: str,
                  uuid_value: str) -> Delete:
    """
    Delete a record in the specified table identified by the given primary
    key name and value.

    >>> delete_record(survey_table, 'survey_id', survey_id)
    <sqlalchemy.sql.dml.Delete object at 0x...>

    Make sure you use a transaction!

    :param table: The SQLAlchemy table
    :param uuid_column_name: The UUID primary key column name
    :param uuid_value: The UUID specifying the record
    :return: A SQLAlchemy Delete object. Execute this!
    """
    column = get_column(table, uuid_column_name)
    return table.delete().where(column == uuid_value)


def get_column(table: Table, column_name: str) -> Column:
    """
    Apparently SQLAlchemy lets you happily c.get a column name that doesn't
    exist.

    :param table: the SQLAlchemy Table
    :param column_name: the name of the column you want to get
    :return: the column
    :raise NoSuchColumnError: if the column does not exist in the table
    """
    if column_name in table.columns:
        return table.c.get(column_name)
    else:
        raise NoSuchColumnError(column_name)


class NoSuchColumnError(Exception):
    pass
