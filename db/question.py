"""Allow access to the question table."""
from sqlalchemy import Table, MetaData, cast, Text, Boolean
from sqlalchemy.engine import RowProxy, ResultProxy
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.functions import max as sqlmax

from db import engine
from db.auth_user import auth_user_table
from db.survey import survey_table, SurveyDoesNotExistError


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

    # Not exactly sure why you need a session to do this
    session = sessionmaker(bind=engine)()
    try:
        query = session.query(sqlmax(question_table.c.sequence_number))
        condition = question_table.c.survey_id == survey_id
        # Without coalesce, this would fall over in the no-questions case.
        coal = coalesce(query.filter(condition).scalar(), 0)
        return engine.execute(coal).scalar() + 1
    finally:
        session.close()


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


def question_select(question_id: str) -> RowProxy:
    """
    Get a record from the question table.

    :param question_id: the UUID of the question
    :return: the corresponding record
    :raise QuestionDoesNotExistError: if the UUID is not in the table
    """
    question = question_table.select().where(
        question_table.c.question_id == question_id).execute().first()
    if question is None:
        raise QuestionDoesNotExistError(question_id)
    return question


class QuestionDoesNotExistError(Exception):
    pass


class MissingMinimalLogicError(Exception):
    pass


def get_questions(survey_id: str,
                  auth_user_id: str=None,
                  email: str=None) -> ResultProxy:
    q_sur_cond = question_table.c.survey_id == survey_table.c.survey_id
    question_survey = question_table.join(survey_table, q_sur_cond)

    if auth_user_id is not None:
        if email is not None:
            raise TypeError('You cannot specify both auth_user_id and email')
        table = question_survey
        cond = and_(question_table.c.survey_id == survey_id,
                    survey_table.c.auth_user_id == auth_user_id)
    elif email is not None:
        j_cond = survey_table.c.auth_user_id == auth_user_table.c.auth_user_id
        table = question_survey.join(auth_user_table, j_cond)
        cond = and_(question_table.c.survey_id == survey_id,
                    auth_user_table.c.email == email)
    else:
        raise TypeError('You must specify either auth_user_id or email')

    questions = table.select().where(cond). \
        order_by('sequence_number asc').execute()
    return questions


def get_questions_no_credentials(survey_id: str) -> ResultProxy:
    """
    Get all the questions for a survey identified by survey_id ordered by
    sequence number.

    :param survey_id: foreign key
    :return: an iterable of the questions (RowProxy)
    """
    select_stmt = question_table.select()
    where_stmt = select_stmt.where(question_table.c.survey_id == survey_id)
    return where_stmt.order_by('sequence_number asc').execute()


def get_required(survey_id: str) -> ResultProxy:
    """
    Get all the required questions for a survey identified by survey_id ordered
    by sequence number.

    :param survey_id: foreign key
    :return: an iterable of the questions (RowProxy)
    """
    select_stmt = question_table.select()
    survey_condition = question_table.c.survey_id == survey_id
    required_condition = cast(cast(question_table.c.logic['required'], Text),
                              Boolean)
    condition = and_(survey_condition, required_condition)
    where_stmt = select_stmt.where(condition)
    return where_stmt.order_by('sequence_number asc').execute()
