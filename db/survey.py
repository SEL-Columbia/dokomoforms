"""Allow access to the survey table."""

from sqlalchemy import Table, MetaData
from sqlalchemy.engine import RowProxy
from sqlalchemy.sql import Insert

from db import engine
from db.auth_user import auth_user_table


survey_table = Table('survey', MetaData(bind=engine), autoload=True)

# TODO: more than one user
AUTH_USER_ID = auth_user_table.select().execute().first().auth_user_id


# TODO: remove hardcoded user
def survey_insert(*, auth_user_id=AUTH_USER_ID, title: str) -> Insert:
    """
    Insert a record into the survey table.

    :param auth_user_id: The UUID of the user.
    :param title: The survey's title
    :return: The Insert object. Execute this!
    """
    return survey_table.insert().values(title=title, auth_user_id=auth_user_id)


def survey_select(survey_id: str) -> RowProxy:
    """
    Get a record from the survey table.

    :param survey_id: the UUID of the survey
    :return: the corresponding record
    """
    return survey_table.select().where(
        survey_table.c.survey_id == survey_id).execute().first()
