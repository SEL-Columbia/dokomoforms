"""Functions for aggregating and interacting with submission data."""
from itertools import takewhile
from numbers import Real
from sqlalchemy import desc
from collections import Iterator

from sqlalchemy.engine import RowProxy, ResultProxy, Connection
from sqlalchemy.sql.functions import GenericFunction, min as sqlmin, \
    max as sqlmax, sum as sqlsum, count as sqlcount
from sqlalchemy.sql import func, and_, select
from tornado.escape import json_decode

from api import json_response
from db import get_column, question_table
from db.answer import answer_table
from db.answer_choice import answer_choice_table
from db.auth_user import get_auth_user_by_email
from db.question import question_select, QuestionDoesNotExistError, \
    get_questions
from db.question_choice import question_choice_select
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


def _jsonify(connection: Connection,
             answer: object,
             question_id: str) -> object:
    """
    This function returns a "nice" representation of an answer which can be
    serialized as JSON.

    :param connection: a SQLAlchemy Connection
    :param answer: a submitted value
    :param type_constraint_name: the UUID of the question
    :return: the nice representation
    """
    type_constraint_name = question_select(connection,
                                           question_id).type_constraint_name
    if type_constraint_name == 'location':
        geo_json = connection.execute(func.ST_AsGeoJSON(answer)).scalar()
        return json_decode(geo_json)['coordinates']
    elif type_constraint_name in {'date', 'time'}:
        return answer.isoformat()
    elif type_constraint_name == 'decimal':
        return float(answer)
    elif type_constraint_name == 'multiple_choice':
        question_choice = question_choice_select(connection, answer)
        return question_choice.choice
    else:
        return answer


def _return_sql(connection: Connection,
                result: object,
                survey_id: str,
                auth_user_id: str,
                question_id: str) -> object:
    """
    Get the result for a _scalar-y function.

    :param connection: a SQLAlchemy Connection
    :param result: the result of the SQL function
    :param survey_id: the UUID of the survey
    :param auth_user_id: the UUID of the user
    :param question_id: the UUID of the question
    :return: the result of the SQL function
    :raise NoSubmissionsToQuestionError: if there are no submissions
    :raise QuestionDoesNotExistError: if the user is not authorized
    """
    if result is None or result == []:
        condition = survey_table.c.survey_id == survey_id
        stmt = select([survey_table]).where(condition)
        proper_id = connection.execute(stmt).first().auth_user_id
        if auth_user_id == proper_id:
            raise NoSubmissionsToQuestionError(question_id)
        raise QuestionDoesNotExistError(question_id)
    return result


def _table_and_column(type_constraint_name: str) -> tuple:
    """
    Get the table and column name relevant for an aggregation.
    :param type_constraint_name: the type constraint of the table
    :return: (table, column_name)
    """
    # Assume that you only want to consider the non-other answers
    if type_constraint_name == 'multiple_choice':
        table = answer_choice_table
        column_name = 'question_choice_id'
    else:
        table = answer_table
        column_name = 'answer_' + type_constraint_name
    return table, column_name


def _get_type_constraint_name(allowable_types: set, question: RowProxy) -> str:
    """
    Return the type_constraint_name for a question if it is an allowable type.
    :param allowable_types: the set of allowable types
    :param question: the SQLAlchemy RowProxy representing the question
    :return: the type_constraint_name
    :raise InvalidTypeForAggregationError: if the type is not allowable
    """
    tcn = question.type_constraint_name
    if tcn not in allowable_types:
        raise InvalidTypeForAggregationError(tcn)
    return tcn


def _get_user_id(connection: Connection,
                 auth_user_id: str,
                 email: str) -> str:
    """
    Get the auth_user_id, whether it or the e-mail address is provided

    :param connection: a SQLAlchemy Connection
    :param auth_user_id: the auth_user_id, if provided
    :param email: the e-mail address, if provided
    :return: the auth_user_id
    """
    user_id, user_email = _get_user(auth_user_id, email)
    # TODO: See if not doing a 3-table join is a performance problem
    if user_email is not None:
        user_id = get_auth_user_by_email(connection, user_email).auth_user_id
    return user_id


def _scalar(connection: Connection,
            question_id: str,
            sql_function: GenericFunction,
            *,
            auth_user_id: str=None,
            email: str=None,
            is_other: bool=False,
            allowable_types: set={'integer', 'decimal'}) -> Real:
    """
    Get a scalar SQL-y value (max, mean, etc) across all submissions to a
    question. You must provide either an auth_user_id or e-mail address.

    :param connection: a SQLAlchemy Connection
    :param question_id: the UUID of the question
    :param sql_function: the SQL function to execute
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user
    :param is_other: whether to look at the "other" responses
    :return: the result of the SQL function
    :raise InvalidTypeForAggregationError: if the type constraint name is bad
    """
    user_id = _get_user_id(connection, auth_user_id, email)

    question = question_select(connection, question_id)

    tcn = _get_type_constraint_name(allowable_types, question)
    if is_other:
        tcn = 'text'

    original_table, column_name = _table_and_column(tcn)
    table = original_table.join(
        question_table,
        original_table.c.question_id == question_table.c.question_id
    ).join(survey_table)

    conds = [question_table.c.question_id == question_id,
             survey_table.c.auth_user_id == user_id]

    column = get_column(original_table, column_name)

    result = connection.execute(select([sql_function(column)]).select_from(
        table).where(and_(*conds))).scalar()

    return _return_sql(connection, result, question.survey_id, user_id,
                       question_id)


class NoSubmissionsToQuestionError(Exception):
    pass


class InvalidTypeForAggregationError(Exception):
    pass


def min(connection: Connection,
        question_id: str,
        auth_user_id: str=None,
        email: str=None) -> dict:
    """
    Get the minimum value of submissions to the specified question. You must
    provide either an auth_user_id or e-mail address.

    :param connection: a SQLAlchemy Connection
    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result
    """
    result = _scalar(connection, question_id, sqlmin,
                     auth_user_id=auth_user_id,
                     email=email,
                     allowable_types={'integer', 'decimal', 'date', 'time'})

    response = json_response(_jsonify(connection, result, question_id))
    response['query'] = 'min'
    return response


def max(connection: Connection,
        question_id: str,
        auth_user_id: str=None,
        email: str=None) -> dict:
    """
    Get the maximum value of submissions to the specified question. You must
    provide either an auth_user_id or e-mail address.

    :param connection: a SQLAlchemy Connection
    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result
    """
    result = _scalar(connection, question_id, sqlmax,
                     auth_user_id=auth_user_id,
                     email=email,
                     allowable_types={'integer', 'decimal', 'date', 'time'})
    response = json_response(_jsonify(connection, result, question_id))
    response['query'] = 'max'
    return response


def sum(connection: Connection,
        question_id: str,
        auth_user_id: str=None,
        email: str=None) -> dict:
    """
    Get the sum of submissions to the specified question. You must
    provide either an auth_user_id or e-mail address.

    :param connection: a SQLAlchemy Connection
    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result
    """
    result = _scalar(connection, question_id, sqlsum,
                     auth_user_id=auth_user_id,
                     email=email)
    response = json_response(result)
    response['query'] = 'sum'
    return response


def count(connection: Connection,
          question_id: str,
          auth_user_id: str=None,
          email: str=None) -> dict:
    """
    Get the number of submissions to the specified question. You must
    provide either an auth_user_id or e-mail address.

    :param connection: a SQLAlchemy Connection
    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result
    """
    types = {'text', 'integer', 'decimal', 'multiple_choice', 'date', 'time',
             'location'}
    regular = _scalar(connection, question_id, sqlcount,
                      auth_user_id=auth_user_id,
                      email=email, allowable_types=types)
    other = _scalar(connection, question_id, sqlcount,
                    auth_user_id=auth_user_id,
                    email=email, is_other=True, allowable_types=types)
    response = json_response(regular + other)
    response['query'] = 'count'
    return response


def avg(connection: Connection,
        question_id: str,
        auth_user_id: str=None,
        email: str=None) -> dict:
    """
    Get the average of submissions to the specified question. You must
    provide either an auth_user_id or e-mail address.

    :param connection: a SQLAlchemy Connection
    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result
    """
    result = _scalar(connection, question_id, func.avg,
                     auth_user_id=auth_user_id,
                     email=email)
    response = json_response(float(result))
    response['query'] = 'avg'
    return response


def stddev_pop(connection: Connection,
               question_id: str,
               auth_user_id: str=None,
               email: str=None) -> dict:
    """
    Get the population standard deviation of submissions to the specified
    question. You must provide either an auth_user_id or e-mail address.

    :param connection: a SQLAlchemy Connection
    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result
    """
    result = _scalar(connection, question_id, func.stddev_pop,
                     auth_user_id=auth_user_id,
                     email=email)
    response = json_response(float(result))
    response['query'] = 'stddev_pop'
    return response


def stddev_samp(connection: Connection,
                question_id: str,
                auth_user_id: str=None,
                email: str=None) -> dict:
    """
    Get the sample standard deviation of submissions to the specified
    question. You must provide either an auth_user_id or e-mail address.

    :param connection: a SQLAlchemy Connection
    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result
    """
    result = _scalar(connection, question_id, func.stddev_samp,
                     auth_user_id=auth_user_id,
                     email=email)
    response = json_response(float(result))
    response['query'] = 'stddev_samp'
    return response


def time_series(connection: Connection,
                question_id: str,
                auth_user_id: str=None,
                email: str=None) -> dict:
    """
    Get a list of submissions to the specified question over time. You must
    provide either an auth_user_id or e-mail address.

    :param connection: a SQLAlchemy Connection
    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :return: a JSON dict containing the result [[times], [values]]
    """
    user_id = _get_user_id(connection, auth_user_id, email)

    allowable_types = {'text', 'integer', 'decimal', 'multiple_choice', 'date',
                       'time', 'location'}

    question = question_select(connection, question_id)

    tcn = _get_type_constraint_name(allowable_types, question)

    # Assume that you only want to consider the non-other answers
    original_table, column_name = _table_and_column(tcn)
    table = original_table.join(
        survey_table,
        original_table.c.survey_id == survey_table.c.survey_id
    ).join(
        submission_table,
        original_table.c.submission_id == submission_table.c.submission_id
    )
    column = get_column(original_table, column_name)

    where_stmt = select(
        [column, submission_table.c.submission_time]
    ).select_from(table).where(
        original_table.c.question_id == question_id
    ).where(
        survey_table.c.auth_user_id == user_id
    )

    result = _return_sql(
        connection,
        connection.execute(where_stmt.order_by('submission_time asc')),
        question.survey_id, auth_user_id, question_id)
    tsr = [[r.submission_time.isoformat(),
            _jsonify(connection, r[column_name], question_id)]
           for r in result]
    time_series_result = tsr
    response = json_response(
        _return_sql(connection, time_series_result, question.survey_id,
                    user_id, question_id))
    response['query'] = 'time_series'
    return response


def bar_graph(connection: Connection,
              question_id: str,
              auth_user_id: str=None,
              email: str=None,
              limit: [int, None]=None,
              count_order: bool=False) -> dict:
    """
    Get a list of the number of times each submission value appears. You must
    provide either an auth_user_id or e-mail address.

    :param connection: a SQLAlchemy Connection
    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user.
    :param limit: a limit on the number of results
    :param count_order: whether to order from largest count to smallest
    :return: a JSON dict containing the result [[values], [counts]]
    """
    user_id = _get_user_id(connection, auth_user_id, email)

    allowable_types = {'text', 'integer', 'decimal', 'multiple_choice', 'date',
                       'time', 'location'}

    question = question_select(connection, question_id)

    tcn = _get_type_constraint_name(allowable_types, question)

    # Assume that you only want to consider the non-other answers
    original_table, column_name = _table_and_column(tcn)
    table = original_table.join(
        question_table,
        original_table.c.question_id == question_table.c.question_id
    ).join(survey_table)

    conds = [question_table.c.question_id == question_id,
             survey_table.c.auth_user_id == user_id]
    column = get_column(original_table, column_name)

    column_query = select(
        [column, sqlcount(column)]
    ).select_from(table).group_by(column)
    ordering = desc(sqlcount(column)) if count_order else column
    ordered_query = column_query.order_by(ordering)

    result = connection.execute(
        ordered_query.where(and_(*conds)).limit(limit)
    )

    result = _return_sql(connection, result, question.survey_id, user_id,
                         question_id)
    bar_graph_result = [[_jsonify(connection, r[0], question_id), r[1]] for r
                        in result]
    response = json_response(
        _return_sql(connection, bar_graph_result, question.survey_id,
                    user_id, question_id))
    response['query'] = 'bar_graph'
    return response


def mode(connection: Connection,
         question_id: str,
         auth_user_id: str=None,
         email: str=None) -> dict:
    """
    Get the mode of answers to the specified question in a list (since there
    may be multiple). You must provide either an auth_user_id or e-mail
    address.

    :param connection: a SQLAlchemy Connection
    :param question_id: the UUID of the question
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user
    :return: a JSON dict containing the result
    """
    bar_graph_top = bar_graph(connection, question_id, auth_user_id, email,
                              None, True)
    result = bar_graph_top['result']
    most_frequent = result[0]
    frequency = most_frequent[1]
    the_mode = takewhile(lambda bar: bar[1] == frequency, result)
    response = json_response(list(val_count[0] for val_count in the_mode))
    response['query'] = 'mode'
    return response


def _get_stats(connection: Connection,
               question: RowProxy,
               auth_user_id: str,
               email: str) -> Iterator:
    """
    Returns a generator of statistics about a question.

    :param connection: a SQLAlchemy Connection
    :param question: the question in a RowProxy object
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user
    """
    for method in (count, min, max, sum, avg, mode, stddev_pop, stddev_samp):
        try:
            result = method(connection,
                            question.question_id,
                            auth_user_id,
                            email)
            yield result
        except InvalidTypeForAggregationError:
            pass
        except NoSubmissionsToQuestionError:
            pass


def _get_question_stats(connection: Connection,
                        questions: ResultProxy,
                        auth_user_id: [str, None],
                        email: [str, None]) -> Iterator:
    """
    Returns a generator of question submission statistics for the given
    questions.

    :param connection: a SQLAlchemy Connection
    :param questions: the questions in a ResultProxy object
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user
    :return: a generator of dicts containing the results
    """
    for question in questions:
        stats = list(_get_stats(connection, question, auth_user_id, email))
        yield {'question': question, 'stats': stats}


def get_question_stats(connection: Connection,
                       survey_id: str,
                       auth_user_id: str=None,
                       email: str=None) -> list:
    """
    Returns a JSON-y list of dicts containing statistics about submissions
    to the questions in the given survey.

    :param connection: a SQLAlchemy Connection
    :param survey_id: the UUID of the survey
    :param auth_user_id: the UUID of the user
    :param email: the e-mail address of the user
    :return: a list containing the results
    """
    user_id = _get_user_id(connection, auth_user_id, email)
    questions = get_questions(connection, survey_id, user_id, None)
    return json_response(
        list(_get_question_stats(connection, questions, user_id, None)))
