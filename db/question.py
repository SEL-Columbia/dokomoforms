"""Allow access to the question table."""
from sqlalchemy import Table, MetaData
from sqlalchemy.engine import RowProxy, ResultProxy
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.functions import max as sqlmax

from db import engine
from db.logical_constraint import insert_logical_constraint_if_necessary


question_table = Table('question', MetaData(bind=engine), autoload=True)


def get_free_sequence_number(survey_id: str) -> int:
    """
    Return the highest existing sequence number + 1 (or 1 if there aren't
    any) associated with the given survey_id.

    :param survey_id: the UUID of the survey
    :return: the free sequence number
    """
    # Sorry for this awful mess of a function... The hoops you have to go
    # through to find the maximum value...

    # Not sure why you need a session
    session = sessionmaker(bind=engine)
    query = session.query(sqlmax(question_table.c.sequence_number))
    condition = question_table.c.survey_id == survey_id
    # Without coalesce, this would fall over in the no-questions case.
    return coalesce(query.filter(condition).scalar(), 0) + 1


def question_insert(*, hint='',
                    sequence_number: int=None,
                    required=False,
                    allow_multiple=False,
                    logical_constraint_name='',
                    title: str,
                    type_constraint_name: str,
                    survey_id: str) -> Insert:
    """
    Insert a record into the question table. A question is associated with a
    survey. Make sure to use a transaction!

    :param hint: an optional hint for the question
    :param sequence_number: the sequence number of the question. If None or
                            not supplied, this defaults to the next available
                            sequence number.
    :param required: whether this is a required question. Default False.
    :param allow_multiple: whether you can give multiple responses. Default
                           False.
    :param logical_constraint_name: The logical constraint (age, volume,
                                    population, etc.)
    :param title: the question title (for example, 'What is your name?')
    :param type_constraint_name: The type of the question. Can be:
                                 text
                                 integer
                                 decimal
                                 multiple_choice
                                 multiple_choice_with_other
                                 date
                                 time
                                 location
                                 note (no answer allowed)
    :param survey_id: the UUID of the survey
    :return: the Insert object. Execute this!
    """
    if sequence_number is None:
        sequence_number = get_free_sequence_number(survey_id)
    tcn = type_constraint_name
    insert_logical_constraint_if_necessary(logical_constraint_name)
    lcn = logical_constraint_name
    return question_table.insert().values(title=title,
                                          hint=hint,
                                          sequence_number=sequence_number,
                                          required=required,
                                          allow_multiple=allow_multiple,
                                          type_constraint_name=tcn,
                                          logical_constraint_name=lcn,
                                          survey_id=survey_id)


def get_question(question_id: str) -> RowProxy:
    """
    Get a record from the question table identified by question_id.

    :param question_id: primary key
    :return: the record
    """
    select_stmt = question_table.select()
    where_stmt = select_stmt.where(question_table.c.question_id == question_id)
    return where_stmt.execute().first()


def get_questions(survey_id: str) -> ResultProxy:
    """
    Get all the questions for a survey identified by survey_id ordered by
    sequence number.

    :param survey_id: foreign key
    :return: an iterable of the questions (RowProxy)
    """
    select_stmt = question_table.select()
    where_stmt = select_stmt.where(question_table.c.survey_id == survey_id)
    return where_stmt.order_by('sequence_number asc').execute()
