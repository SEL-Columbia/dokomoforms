"""Allow access to the submission table."""
from collections import Iterator
from datetime import datetime
from sqlalchemy import select

from sqlalchemy.engine import RowProxy, ResultProxy, Connection
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.functions import count

from dokomoforms.db import get_column, submission_table, answer_table, \
    auth_user_table, survey_table


def submission_insert(*,
                      survey_id: str,
                      submitter: str,
                      submitter_email: str,
                      submission_time: [str, datetime]=None,
                      save_time: [str, datetime]=None) -> Insert:
    """
    Insert a record into the submission table.

    :param submitter: name
    :param survey_id: The UUID of the survey.
    :param submission_time: the time of the submission. Default now()
    :param save_time: the time of survey completion. Default now()
    :return: The Insert object. Execute this!
    """
    values = {
              'survey_id': survey_id,
              'submitter': submitter,
              'submitter_email': submitter
    }

    if submission_time is not None:
        values['submission_time'] = submission_time
    if save_time is not None:
        values['save_time'] = save_time
    return submission_table.insert().values(values)


def submission_select(connection: Connection,
                      submission_id: str,
                      auth_user_id: str=None,
                      email: str=None) -> RowProxy:
    """
    Get a record from the submission table. You must supply either the
    auth_user_id or the email.

    :param connection: a SQLAlchemy Connection
    :param submission_id: the UUID of the submission
    :param auth_user_id: the UUID of the user
    :param email: the user's e-mail address
    :return: the corresponding records
    :raise SubmissionDoesNotExistError: if the submission_id is not in the
                                        table
    """

    table = submission_table.join(survey_table)
    conds = [submission_table.c.submission_id == submission_id]

    if auth_user_id is not None:
        if email is not None:
            raise TypeError('You cannot specify both auth_user_id and email')
        conds.append(survey_table.c.auth_user_id == auth_user_id)
    elif email is not None:
        table = table.join(auth_user_table)
        conds.append(auth_user_table.c.email == email)
    else:
        raise TypeError('You must specify either auth_user_id or email')

    submission = connection.execute(
        select([submission_table]).select_from(table).where(
            and_(*conds))).first()
    if submission is None:
        raise SubmissionDoesNotExistError(submission_id)
    return submission


def _get_filtered_ids(connection: Connection, filters: list) -> Iterator:
    """
    Given a list of filters like
    { 'question_id': <question_id>,
      '<type_constraint_name>': <value> },
    yield the submission_id values that pass the filters

    :param connection: a SQLAlchemy Connection
    :param filters: a list of filters consisting of answers to questions
    """
    for filter_pair in filters:
        question_id = filter_pair.pop('question_id')
        type_constraint = list(filter_pair.keys())[0]  # TODO: better way...?
        value = filter_pair[type_constraint]
        answers = connection.execute(
            select([answer_table]).where(
                answer_table.c.question_id == question_id
            ).where(get_column(answer_table, type_constraint) == value))
        for answer in answers:
            yield answer.submission_id


def get_submissions_by_email(connection: Connection,
                             email: str,
                             survey_id: str=None,
                             submitters: Iterator=None,
                             filters: list=None,
                             order_by: str=None,
                             direction: str='ASC',
                             limit: int=None) -> ResultProxy:
    """
    Get submissions to a survey.

    :param connection: a SQLAlchemy Connection
    :param survey_id: the UUID of the survey
    :param email: the e-mail address of the user
    :param submitters: if supplied, filters results by all given submitters
    :param filters: if supplied, filters results by answers
    :param order_by: if supplied, the column for the ORDER BY clause
    :param direction: optional sort direction for order_by (default ASC)
    :param limit: if supplied, the limit to apply to the number of results
    :return: an iterable of the submission records
    """

    table = submission_table.join(survey_table).join(auth_user_table)
    
    conds = [auth_user_table.c.email == email]
    
    if survey_id:
        conds.append(submission_table.c.survey_id == survey_id)

    if submitters is not None:
        conds.append(submission_table.c.submitter.in_(submitters))
    if filters is not None:
        filtered = set(_get_filtered_ids(connection, filters))
        conds.append(submission_table.c.submission_id.in_(filtered))
    if order_by is None:
        order_by = 'submission_time'
    return connection.execute(
        select(
            [submission_table]
        ).select_from(
            table
        ).where(
            and_(*conds)
        ).order_by(
            '{} {}'.format(order_by, direction)
        ).limit(
            limit
        )
    )


def get_number_of_submissions(connection: Connection, survey_id: str) -> int:
    """
    Return the number of submissions for a given survey

    :param connection: a SQLAlchemy Connection
    :param survey_id: the UUID of the survey
    :return: the corresponding number of submissions
    """
    return connection.execute(select([count()]).where(
        submission_table.c.survey_id == survey_id)).scalar()


class SubmissionDoesNotExistError(Exception):
    pass
