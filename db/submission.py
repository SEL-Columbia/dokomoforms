"""Allow access to the submission table."""
from collections import Iterator
from sqlalchemy import Table, MetaData
from datetime import datetime

from sqlalchemy.engine import RowProxy, ResultProxy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.elements import and_

from db import engine, get_column
from db.answer import answer_table
from db.auth_user import auth_user_table
from db.survey import survey_table


submission_table = Table('submission', MetaData(bind=engine), autoload=True)


def submission_insert(*,
                      submitter: str,
                      survey_id: str,
                      submission_time: [str, datetime]=None,
                      field_update_time: [str, datetime]=None) -> Insert:
    """
    Insert a record into the submission table.

    :param submitter: name
    :param survey_id: The UUID of the survey.
    :param submission_time: the time of the submission. Default now()
    :param field_update_time: the time of the update in the field. Default
                              now()
    :return: The Insert object. Execute this!
    """
    values = {'submitter': submitter,
              'survey_id': survey_id}
    if submission_time is not None:
        values['submission_time'] = submission_time
    if field_update_time is not None:
        values['field_update_time'] = field_update_time
    return submission_table.insert().values(values)


def submission_select(submission_id: str,
                      auth_user_id: str=None,
                      email: str=None) -> RowProxy:
    """
    Get a record from the submission table. You must supply either the
    auth_user_id or the email.

    :param submission_id: the UUID of the submission
    :param auth_user_id: the UUID of the user
    :param email: the user's e-mail address
    :return: the corresponding records
    :raise SubmissionDoesNotExistError: if the submission_id is not in the
                                        table
    """

    sub_sur_cond = submission_table.c.survey_id == survey_table.c.survey_id
    submission_survey = submission_table.join(survey_table, sub_sur_cond)

    if auth_user_id is not None:
        if email is not None:
            raise TypeError('You cannot specify both auth_user_id and email')
        table = submission_survey
        cond = and_(submission_table.c.submission_id == submission_id,
                    survey_table.c.auth_user_id == auth_user_id)
    elif email is not None:
        j_cond = survey_table.c.auth_user_id == auth_user_table.c.auth_user_id
        table = submission_survey.join(auth_user_table, j_cond)
        cond = and_(submission_table.c.submission_id == submission_id,
                    auth_user_table.c.email == email)
    else:
        raise TypeError('You must specify either auth_user_id or email')

    submission = table.select(use_labels=True).where(cond).execute().first()
    if submission is None:
        raise SubmissionDoesNotExistError(submission_id)
    return submission


def _get_filtered_ids(filters: list) -> Iterator:
    """
    Given a list of filters like
    { 'question_id': <question_id>,
      '<type_constraint_name>': <value> },
    yield the submission_id values that pass the filters
    :param filters: a list of filters consisting of answers to questions
    """
    for filter_pair in filters:
        question_id = filter_pair.pop('question_id')
        type_constraint = list(filter_pair.keys())[0]  # TODO: better way...?
        value = filter_pair[type_constraint]
        answers = answer_table.select().where(
            and_(answer_table.c.question_id == question_id,
                 get_column(answer_table, type_constraint) == value)).execute()
        for answer in answers:
            yield answer.submission_id


def get_submissions_by_email(survey_id: str,
                             email: str,
                             submitters: Iterator=None,
                             filters: list=None) -> ResultProxy:
    """
    Get submissions to a survey.

    :param survey_id: the UUID of the survey
    :param email: the e-mail address of the user
    :param submitters: if supplied, filters results by all given submitters
    :param filters: if supplied, filters results by answers
    :return: an iterable of the submission records
    """

    survey_condition = submission_table.c.survey_id == survey_table.c.survey_id
    table = submission_table.join(survey_table, survey_condition)
    user_cond = survey_table.c.auth_user_id == auth_user_table.c.auth_user_id
    table = table.join(auth_user_table, user_cond)

    conditions = [submission_table.c.survey_id == survey_id,
                  auth_user_table.c.email == email]
    if submitters is not None:
        conditions.append(submission_table.c.submitter.in_(submitters))
    if filters is not None:
        filtered = set(_get_filtered_ids(filters))
        conditions.append(submission_table.c.submission_id.in_(filtered))
    return table.select().where(and_(*conditions)).order_by(
        'submission_time').execute()


def get_number_of_submissions(survey_id: str) -> int:
    """
    Return the number of submissions for a given survey
    :param survey_id: the UUID of the survey
    :return: the corresponding number of submissions
    """
    session = sessionmaker(bind=engine)()
    try:
        query = session.query(submission_table)
        return query.filter(submission_table.c.survey_id == survey_id).count()
    finally:
        session.close()


class SubmissionDoesNotExistError(Exception):
    pass
