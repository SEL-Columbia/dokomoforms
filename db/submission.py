"""Allow access to the submission table."""
from sqlalchemy import Table, MetaData
from sqlalchemy.sql.dml import Insert

from db import engine


submission_table = Table('submission', MetaData(bind=engine), autoload=True)


def submission_insert(*, latitude: float, longitude: float, submitter: str,
                      survey_id: str) -> Insert:
    """
    Insert a record into the submission table.

    :param latitude: degrees
    :param longitude: degrees
    :param submitter: name
    :param survey_id: The UUID of the survey.
    :return: The Insert object. Execute this!
    """
    values = {'latitude': latitude,
              'longitude': longitude,
              'submitter': submitter,
              'survey_id': survey_id}
    return submission_table.insert().values(values)
