"""Functions for aggregating and interacting with submission data."""
from numbers import Real

from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.functions import GenericFunction, min as sqlmin, \
    max as sqlmax, sum as sqlsum, count as sqlcount
from sqlalchemy.sql import func, and_

from db import engine
from db.answer import answer_table
from db.answer_choice import answer_choice_table
from db.auth_user import get_auth_user_by_email
from db.question import question_select, QuestionDoesNotExistError
from db.submission import submission_table
from db.survey import survey_table


def _get_user(auth_user_id: str=None, email: str=None):
    """
    For functions that allow you to specify either auth_user_id or email,
    this function returns (auth_user_id, email), one of which is guaranteed
    to be None

    :param auth_user_id: the UUID of the user
    :param email: the user's e-mail address
    :return: (auth_user_id, email), one of which is None
    :raise TypeError: if neither or both parameters are supplied
    """
    if (auth_user_id is None) != (email is None):
        return auth_user_id, email
    raise TypeError('You must specify either auth_user_id or email')


def _return_sql(result: Real,
                survey_id: str,
                auth_user_id: str,
                question_id: str) -> Real:
    """
    Get the result for a _scalar-y function.

    :param result: the result of the SQL function
    :param survey_id: the UUID of the survey
    :param auth_user_id: the UUID of the user
    :param question_id: the UUID of the question
    :return: the result of the SQL function
    :raise NoSubmissionsToQuestionError: if there are no submissions
    :raise QuestionDoesNotExistError: if the user is not authorized
    """
    if result is None:
        condition = survey_table.c.survey_id == survey_id
        stmt = survey_table.select().where(condition)
        proper_id = stmt.execute().first().auth_user_id
        if auth_user_id == proper_id:
            raise NoSubmissionsToQuestionError(question_id)
        raise QuestionDoesNotExistError(question_id)
    return result


def _scalar(question_id: str,
            sql_function: GenericFunction,
            *,
            auth_user_id: str=None,
            email: str=None,
            is_other: bool=False,
            allowable_types: set={'integer', 'decimal'}) -> Real:
    """
    Get a scalar SQL-y value (max, mean, etc) across all submissions to a
    question. You must provide either an auth_user_id or e-mail address.

    :param question_id: the UUID of the question
    :param sql_function: the SQL function to execute
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user
    :param is_other: whether to look at the "other" responses
    :return: the result of the SQL function
    :raise InvalidTypeForAggregationError: if the type constraint name is bad
    """
    user_id, user_email = _get_user(auth_user_id, email)
    # TODO: See if not doing a 3-table join is a performance problem
    if user_email is not None:
        user_id = get_auth_user_by_email(user_email).auth_user_id

    question = question_select(question_id)

    tcn = question.type_constraint_name
    if tcn not in allowable_types:
        raise InvalidTypeForAggregationError(tcn)
    if is_other:
        tcn = 'text'

    if tcn == 'multiple_choice':
        table = answer_choice_table
        column_name = 'question_choice_id'
    else:
        table = answer_table
        column_name = 'answer_' + tcn
    join_condition = table.c.survey_id == survey_table.c.survey_id
    condition = (table.c.question_id == question_id,
                 survey_table.c.auth_user_id == user_id)
    column = table.c.get(column_name)

    session = sessionmaker(bind=engine)()
    try:
        column_query = session.query(sql_function(column))
        join_query = column_query.join(survey_table, join_condition)
        result = join_query.filter(*condition).scalar()
    finally:
        session.close()

    return _return_sql(result, question.survey_id, user_id, question_id)


class NoSubmissionsToQuestionError(Exception):
    pass


class InvalidTypeForAggregationError(Exception):
    pass


def min(question_id: str, auth_user_id: str=None, email: str=None) -> dict:
    """
    Get the minimum value of submissions to the specified question. You must
    provide either an auth_user_id or e-mail address.

    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result
    """
    return {'result': _scalar(question_id, sqlmin, auth_user_id=auth_user_id,
                              email=email,
                              allowable_types={'integer',
                                               'decimal',
                                               'date',
                                               'time'}),
            'query': 'min'}


def max(question_id: str, auth_user_id: str=None, email: str=None) -> dict:
    """
    Get the maximum value of submissions to the specified question. You must
    provide either an auth_user_id or e-mail address.

    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result
    """
    return {'result': _scalar(question_id, sqlmax, auth_user_id=auth_user_id,
                              email=email,
                              allowable_types={'integer',
                                               'decimal',
                                               'date',
                                               'time'}),
            'query': 'max'}


def sum(question_id: str, auth_user_id: str=None, email: str=None) -> dict:
    """
    Get the sum of submissions to the specified question. You must
    provide either an auth_user_id or e-mail address.

    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result
    """
    return {'result': _scalar(question_id, sqlsum, auth_user_id=auth_user_id,
                              email=email),
            'query': 'sum'}


def count(question_id: str, auth_user_id: str=None, email: str=None) -> dict:
    """
    Get the number of submissions to the specified question. You must
    provide either an auth_user_id or e-mail address.

    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result
    """
    types = {'text', 'integer', 'decimal', 'multiple_choice', 'date', 'time',
             'location'}
    regular = _scalar(question_id, sqlcount, auth_user_id=auth_user_id,
                      email=email, allowable_types=types)
    other = _scalar(question_id, sqlcount, auth_user_id=auth_user_id,
                    email=email, is_other=True, allowable_types=types)
    return {'result': regular + other,
            'query': 'count'}


def avg(question_id: str, auth_user_id: str=None, email: str=None) -> dict:
    """
    Get the average of submissions to the specified question. You must
    provide either an auth_user_id or e-mail address.

    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result
    """
    result = _scalar(question_id, func.avg,
                     auth_user_id=auth_user_id,
                     email=email)
    return {'result': float(result),
            'query': 'avg'}


def stddev_pop(question_id: str,
               auth_user_id: str=None, email: str=None) -> dict:
    """
    Get the population standard deviation of submissions to the specified
    question. You must provide either an auth_user_id or e-mail address.

    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result
    """
    result = _scalar(question_id, func.stddev_pop,
                     auth_user_id=auth_user_id,
                     email=email)
    return {'result': float(result),
            'query': 'stddev_pop'}


def stddev_samp(question_id: str,
                auth_user_id: str=None, email: str=None) -> dict:
    """
    Get the sample standard deviation of submissions to the specified
    question. You must provide either an auth_user_id or e-mail address.

    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result
    """
    result = _scalar(question_id, func.stddev_samp,
                     auth_user_id=auth_user_id,
                     email=email)
    return {'result': float(result),
            'query': 'stddev_samp'}


# def mode(question_id: str, auth_user_id: str=None, email: str=None) -> dict:
# """
# Get the mode of answers to the specified question, or the first one if
# there are multiple equally-frequent results. You must provide either an
# auth_user_id or e-mail address.
#
# :param question_id: the UUID of the question
# :param auth_user_id: the UUID of the user
# :param email: the e-mail address of the user
#     :return: a JSON dict containing the result
#     """
#     user_id, user_email = _get_user(auth_user_id, email)
#     # TODO: See if not doing a 3-table join is a performance problem
#     if user_email is not None:
#         user_id = get_auth_user_by_email(user_email).auth_user_id
#
#     allowable_types = {'text', 'integer', 'decimal', 'multiple_choice',
# 'date',
#                        'time', 'location'}
#
#     question = question_select(question_id)
#     tcn = question.type_constraint_name
#     if tcn not in allowable_types:
#         raise InvalidTypeForAggregationError(tcn)
#
#     # Assume that you only want to consider the non-other answers for the
# mode
#
#     if tcn == 'multiple_choice':
#         table_name = 'answer_choice'
#         column_name = 'question_choice_id'
#     else:
#         table_name = 'answer'
#         column_name = 'answer_' + tcn
#
#     query = """SELECT MODE() WITHIN GROUP (ORDER BY {0}) FROM {1} JOIN
#     survey ON {1}.survey_id = survey.survey_id WHERE auth_user_id = '{2}'
#     AND question_id = '{3}'"""
#
#     result = engine.execute(
#         query.format(column_name, table_name, user_id, question_id)).scalar()
#
#     final = _return_scalar(result, question.survey_id, user_id, question_id)
#
#     return {'result': final, 'query': 'mode'}

def time_series(question_id: str, auth_user_id: str=None,
                email: str=None) -> dict:
    """
    Get a list of submissions to the specified question over time. You must
    provide either an auth_user_id or e-mail address.

    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result
    """
    user_id, user_email = _get_user(auth_user_id, email)
    # TODO: See if not doing a 3-table join is a performance problem
    if user_email is not None:
        user_id = get_auth_user_by_email(user_email).auth_user_id

    allowable_types = {'text', 'integer', 'decimal', 'multiple_choice', 'date',
                       'time', 'location'}

    question = question_select(question_id)
    tcn = question.type_constraint_name
    if tcn not in allowable_types:
        raise InvalidTypeForAggregationError(tcn)

    # Assume that you only want to consider the non-other answers for the mode
    if tcn == 'multiple_choice':
        table = answer_choice_table
        column_name = 'question_choice_id'
    else:
        table = answer_table
        column_name = 'answer_' + tcn

    survey_condition = table.c.survey_id == survey_table.c.survey_id
    join_table = table.join(survey_table, survey_condition)
    submission_cond = table.c.submission_id == submission_table.c.submission_id
    join_table = join_table.join(submission_table, submission_cond)

    where_stmt = join_table.select().where(
        and_(table.c.question_id == question_id,
             survey_table.c.auth_user_id == user_id))
    result = _return_sql(where_stmt.order_by('submission_time asc').execute(),
                         question.survey_id, auth_user_id, question_id)
    # transpose the result into two lists: time and value
    genexp = ((r.submission_time.isoformat(), r[column_name]) for r in result)
    time_series_result = list(zip(*genexp))
    return {'result': time_series_result, 'query': 'time_series'}
