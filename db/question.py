"""Allow access to the question table."""
from sqlalchemy import select, Integer
from sqlalchemy import cast, Text, Boolean

from sqlalchemy.engine import RowProxy, ResultProxy, Connection
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.functions import max as sqlmax, coalesce

from db import question_table
from db.auth_user import auth_user_table
from db.survey import survey_table


def get_free_sequence_number(connection: Connection, survey_id: str) -> int:
    """
    Return the highest existing sequence number + 1 (or 1 if there aren't
    any) associated with the given survey_id.

    :param connection: a SQLAlchemy Connection
    :param survey_id: the UUID of the survey
    :return: the free sequence number
    """
    sequence_number = question_table.c.sequence_number
    return connection.execute(select(
        [coalesce(sqlmax(sequence_number, type_=Integer), 0)])).scalar() + 1


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
                    sequence_number: int,
                    hint: str,
                    allow_multiple: bool,
                    logic: dict,
                    question_title: str,
                    type_constraint_name: str,
                    question_to_sequence_number: int,
                    survey_id: str) -> Insert:
    """
    Insert a record into the question table. A question is associated with a
    survey. Make sure to use a transaction!

    :param choices: unused parameter. convenient for taking parameters from
                    the front-end
    :param branches: unused parameter, convenient for taking parameters from
                     the front-end
    :param hint: an optional hint for the question
    :param sequence_number: the sequence number of the question
    :param allow_multiple: whether you can give multiple responses. Default
                           False.
    :param logic: the logical constraint (min or max value, etc) as JSON
    :param question_title: the question title (for example, 'What is your
    name?')
    :param type_constraint_name: The type of the question. Can be:
                                 text
                                 integer
                                 decimal
                                 multiple_choice
                                 date
                                 time
                                 location
                                 note (no answer allowed)
    :param question_to_sequence_number: the sequence number of the subequent
                                        question
    :param survey_id: the UUID of the survey
    :return: the Insert object. Execute this!
    """
    if logic is None:
        raise TypeError('logic must not be None')
    tcn = type_constraint_name
    # These values must be provided in the insert statement
    values = {'question_title': question_title,
              'type_constraint_name': tcn,
              'survey_id': survey_id,
              'sequence_number': sequence_number,
              'question_to_sequence_number': question_to_sequence_number}
    # These values will only be inserted if they were supplied (since they
    # have default values in the db)
    values = _add_optional_values(values, hint=hint,
                                  allow_multiple=allow_multiple, logic=logic)
    return question_table.insert().values(values)


def question_select(connection: Connection, question_id: str) -> RowProxy:
    """
    Get a record from the question table.

    :param connection: a SQLAlchemy Connection
    :param question_id: the UUID of the question
    :return: the corresponding record
    :raise QuestionDoesNotExistError: if the UUID is not in the table
    """
    question = connection.execute(select([question_table]).where(
        question_table.c.question_id == question_id)).first()
    if question is None:
        raise QuestionDoesNotExistError(question_id)
    return question


class QuestionDoesNotExistError(Exception):
    pass


class MissingMinimalLogicError(Exception):
    pass


def get_questions(connection: Connection,
                  survey_id: str,
                  auth_user_id: str=None,
                  email: str=None) -> ResultProxy:
    """
    Get all the questions for a survey identified by survey_id ordered by
    sequence number restricted by auth_user.

    :param connection: a SQLAlchemy Connection
    :param survey_id: the UUID of the survey
    :param auth_user_id: the UUID of the user
    :param email: the user's e-mail address
    :return: an iterable of the questions (RowProxy)
    """
    # q_sur_cond = question_table.c.survey_id == survey_table.c.survey_id
    # question_survey = question_table.join(survey_table, q_sur_cond)

    table = question_table.join(survey_table)
    conds = [question_table.c.survey_id == survey_id]

    if auth_user_id is not None:
        if email is not None:
            raise TypeError('You cannot specify both auth_user_id and email')
        conds.append(survey_table.c.auth_user_id == auth_user_id)
    elif email is not None:
        table = table.join(auth_user_table)
        conds.append(auth_user_table.c.email == email)
    else:
        raise TypeError('You must specify either auth_user_id or email')

    questions = connection.execute(
        select([question_table]).select_from(table).where(
            and_(*conds)).order_by('sequence_number asc'))
    return questions


def get_questions_no_credentials(connection: Connection,
                                 survey_id: str) -> ResultProxy:
    """
    Get all the questions for a survey identified by survey_id ordered by
    sequence number.

    :param connection: a SQLAlchemy Connection
    :param survey_id: foreign key
    :return: an iterable of the questions (RowProxy)
    """
    select_stmt = select([question_table])
    where_stmt = select_stmt.where(question_table.c.survey_id == survey_id)
    return connection.execute(where_stmt.order_by('sequence_number asc'))


def get_required(connection: Connection, survey_id: str) -> ResultProxy:
    """
    Get all the required questions for a survey identified by survey_id ordered
    by sequence number.

    :param connection: a SQLAlchemy Connection
    :param survey_id: foreign key
    :return: an iterable of the questions (RowProxy)
    """
    select_stmt = select([question_table])
    survey_condition = question_table.c.survey_id == survey_id
    required_condition = cast(cast(
        question_table.c.logic['required'], Text), Boolean)
    where_stmt = select_stmt.where(survey_condition).where(required_condition)
    return connection.execute(where_stmt.order_by('sequence_number asc'))
