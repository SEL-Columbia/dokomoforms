"""Allow access to the survey table."""
import re
from collections import Iterator
from sqlalchemy import Text

from sqlalchemy.engine import RowProxy, ResultProxy, Connection
from sqlalchemy.sql import Insert, and_, cast, select, exists

from dokomoforms.db import survey_table, auth_user_table


def survey_insert(*, auth_user_id: str, survey_title: str) -> Insert:
    """
    Insert a record into the survey table.

    :param auth_user_id: The UUID of the user.
    :param survey_title: The survey's title
    :return: The Insert object. Execute this!
    """
    return survey_table.insert().values(survey_title=survey_title,
                                        auth_user_id=auth_user_id)


def get_surveys_by_email(connection: Connection,
                         email: str,
                         limit: int=None) -> ResultProxy:
    """
    Get all surveys for the specified user ordered by creation time.

    :param connection: a SQLAlchemy Connection
    :param email: the e-mail address of the user
    :param limit: how many results to return. Defaults to all
    :return: the corresponding survey records
    """
    table = survey_table.join(auth_user_table)
    return connection.execute(
        select([survey_table]).select_from(table).limit(limit).where(
            auth_user_table.c.email == email
        ).order_by('created_on asc')).fetchall()


def get_survey_id_from_prefix(connection: Connection,
                              survey_prefix: str) -> str:
    """
    Return the survey UUID that is identified uniquely by the given prefix.

    :param connection: a SQLAlchemy Connection
    :param survey_prefix: a string of characters that could be the prefix to
                          a UUID
    :return: the full UUID
    :raise SurveyPrefixDoesNotIdentifyASurvey: if the given prefix identifies
                                               0 or more than 1 survey
    """
    if len(survey_prefix) < 8:
        raise SurveyPrefixTooShortError(survey_prefix)
    survey_id_text = cast(survey_table.c.survey_id, Text)
    cond = survey_id_text.like('{}%'.format(survey_prefix))
    surveys = connection.execute(
        select([survey_table]).limit(2).where(cond)).fetchall()
    if len(surveys) == 1:
        return surveys[0].survey_id
    raise SurveyPrefixDoesNotIdentifyASurveyError(survey_prefix)


def display(connection: Connection, survey_id: str) -> RowProxy:
    """
    Only use this to display a single survey for submission purposes.

    :param connection: a SQLAlchemy Connection
    :param survey_id: the UUID of the survey
    :return: the corresponding record
    :raise SurveyDoesNotExistError: if the UUID is not in the table
    """
    survey = connection.execute(select([survey_table]).where(
        survey_table.c.survey_id == survey_id)).first()
    if survey is None:
        raise SurveyDoesNotExistError(survey_id)
    return survey


def survey_select(connection: Connection,
                  survey_id: str,
                  auth_user_id: str=None,
                  email: str=None) -> RowProxy:
    """
    Get a record from the survey table. You must supply either the
    auth_user_id or the email.

    :param connection: a SQLAlchemy Connection
    :param survey_id: the UUID of the survey
    :param auth_user_id: the UUID of the user
    :param email: the user's e-mail address
    :return: the corresponding record
    :raise SurveyDoesNotExistError: if the UUID is not in the table
    """
    table = survey_table
    conds = [survey_table.c.survey_id == survey_id]

    if auth_user_id is not None:
        if email is not None:
            raise TypeError('You cannot specify both auth_user_id and email')
        conds.append(survey_table.c.auth_user_id == auth_user_id)
    elif email is not None:
        table = table.join(auth_user_table)
        conds.append(auth_user_table.c.email == email)
    else:
        raise TypeError('You must specify either auth_user_id or email')

    survey = connection.execute(select([survey_table]).select_from(
        table).where(and_(*conds))).first()
    if survey is None:
        raise SurveyDoesNotExistError(survey_id)
    return survey


def get_email_address(connection: Connection,
                      survey_id: str) -> str:
    """
    Dangerous function! Do not use this to circumvent the restriction
    that a survey can only be seen by its owner!

    Gets the e-mail address associated with a survey.

    :param connection: a SQLAlchemy Connection
    :param survey_id: the UUID of the survey
    :return: the user's e-mail address
    """
    table = auth_user_table.join(survey_table)
    return connection.execute(
        select([auth_user_table.c.email]).select_from(table).where(
            survey_table.c.survey_id == survey_id)).first().email


def _conflicting(title: str, surveys: ResultProxy) -> Iterator:
    """
    Get the appended number from conflicting titles in the survey table.

    :param title: the survey title in question
    :param surveys: the surveys from the table
    :return: the appended numbers from conflicting titles
    """
    for survey in surveys:
        # Match things like "title(1)"
        pattern = r'{}\((\d+)\)'.format(title)
        match = re.match(pattern, survey.survey_title)
        if match:
            number = match.groups()[0]
            yield int(number)


def get_free_title(connection: Connection,
                   title: str,
                   auth_user_id: str) -> str:
    """
    Get a good version of the title to be inserted into the survey table. If
    the title as given already exists, this function will append a number.
    For example, when the title is "survey":
    1. "survey" not in table -> "survey"
    2. "survey" in table     -> "survey(1)"
    3. "survey(1)" in table  -> "survey(2)"

    :param connection: a SQLAlchemy Connection
    :param title: the survey title
    :param auth_user_id: the user's UUID
    :return: a title that can be inserted safely
    """

    (does_exist, ), = connection.execute(
        select((exists().where(
            survey_table.c.survey_title == title
        ).where(survey_table.c.auth_user_id == auth_user_id),)))
    if not does_exist:
        return title
    similar_surveys = connection.execute(
        select([survey_table]).where(
            survey_table.c.survey_title.like(title + '%')
        ).where(
            survey_table.c.auth_user_id == auth_user_id
        )
    ).fetchall()
    conflicts = list(_conflicting(title, similar_surveys))
    free_number = max(conflicts) + 1 if len(conflicts) else 1
    return title + '({})'.format(free_number)


class SurveyDoesNotExistError(Exception):
    pass


class SurveyAlreadyExistsError(Exception):
    pass


class SurveyPrefixDoesNotIdentifyASurveyError(Exception):
    pass


class SurveyPrefixTooShortError(Exception):
    pass


class IncorrectQuestionIdError(Exception):
    pass
