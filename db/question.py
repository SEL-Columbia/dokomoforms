"""Allow access to the question table."""
from sqlalchemy import Table, MetaData
from sqlalchemy.engine import RowProxy, ResultProxy
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.functions import max as sqlmax

from db import engine


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
    session = sessionmaker(bind=engine)()
    query = session.query(sqlmax(question_table.c.sequence_number))
    condition = question_table.c.survey_id == survey_id
    # Without coalesce, this would fall over in the no-questions case.
    coal = coalesce(query.filter(condition).scalar(), 0)
    return engine.execute(coal).scalar() + 1


def _add_optional_values(values: dict, **kwargs) -> dict:
    """
    Given a dict of values for the insert statement, add entries for the
    values which are not None.

    :param values: the existing dict
    :param kwargs: the values to add if not None
    :return: the dict with the values added
    """
    result = values.copy()
    for key, value in kwargs.items():
        if value is not None:
            result[key] = value
    return result


def question_insert(*,
                    choices: list=None,
                    branches: list=None,
                    sequence_number: int=None,
                    hint: str,
                    required: bool,
                    allow_multiple: bool,
                    logic: dict,
                    title: str,
                    type_constraint_name: str,
                    survey_id: str) -> Insert:
    """
    Insert a record into the question table. A question is associated with a
    survey. Make sure to use a transaction!

    :param choices: unused parameter. convenient for taking parameters from
                    the front-end
    :param branches: unused parameter, convenient for taking parameters from
                     the front-end
    :param hint: an optional hint for the question
    :param sequence_number: the sequence number of the question. If None or
                            not supplied, this defaults to the next available
                            sequence number.
    :param required: whether this is a required question. Default False.
    :param allow_multiple: whether you can give multiple responses. Default
                           False.
    :param logic: the logical constraint (min or max value, etc) as JSON
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

    # If no sequence number is supplied, pick up the next available one
    if sequence_number is None:
        sequence_number = get_free_sequence_number(survey_id)
    tcn = type_constraint_name
    # These values must be provided in the insert statement
    values = {'title': title,
              'type_constraint_name': tcn,
              'survey_id': survey_id,
              'sequence_number': sequence_number}
    # These values will only be inserted if they were supplied (since they
    # have default values in the db)
    values = _add_optional_values(values, hint=hint, required=required,
                                  allow_multiple=allow_multiple, logic=logic)
    return question_table.insert().values(values)


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
