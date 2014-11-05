"""Allow access to the submission table."""

from sqlalchemy import Table, MetaData

from sqlalchemy.engine import RowProxy, ResultProxy
from sqlalchemy.sql.dml import Insert

from db import engine


submission_table = Table('submission', MetaData(bind=engine), autoload=True)


def submission_insert(*, submitter: str, survey_id: str) -> Insert:
    """
    Insert a record into the submission table.

    :param submitter: name
    :param survey_id: The UUID of the survey.
    :return: The Insert object. Execute this!
    """
    values = {'submitter': submitter,
              'survey_id': survey_id}
    return submission_table.insert().values(values)


def submission_select(submission_id: str) -> RowProxy:
    """
    Get a record from the submission table.

    :param submission_id: the UUID of the submission
    :return: the corresponding records
    :raise SubmissionDoesNotExistError: if the submission_id is not in the
                                        table
    """
    submission = submission_table.select().where(
        submission_table.c.submission_id == submission_id).execute().first()
    if submission is None:
        raise SubmissionDoesNotExistError(submission_id)
    return submission


def get_submissions(survey_id: str) -> ResultProxy:
    """
    Get submissions to a survey.

    :param survey_id: the UUID of the survey
    :return: an iterable of the submission records
    """
    return submission_table.select().where(
        submission_table.c.survey_id == survey_id).execute()


class SubmissionDoesNotExistError(Exception):
    pass
