"""Allow access to the answer table."""
from sqlalchemy import Table, MetaData, text
from sqlalchemy.engine import ResultProxy, RowProxy
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql import func

from db import engine
from db.question import get_question


answer_table = Table('answer', MetaData(bind=engine), autoload=True)


def _sanitize_answer(answer: str, type_constraint_name: str) -> str:
    """
    Certain question types require some massaging in order to go into the
    database properly. This function does that massaging.

    location: uses the ST_GeomFromText function in the database. The input
    must be in the form 'LON LAT'. Uses SRID 4326 (AKA WGS 84
    http://en.wikipedia.org/wiki/World_Geodetic_System), which should work with
    the coordinates given by Android phones.

    :param answer: The answer value.
    :param type_constraint_name: The type constraint for the question
    :return: The answer in a form that is insertable
    """
    if type_constraint_name == 'location':
        return text("ST_GeomFromText('POINT({})', 4326)".format(answer))
    return answer


def answer_insert(*,
                  answer,
                  question_id: str,
                  submission_id: str,
                  survey_id: str) -> Insert:
    """
    Insert a record into the answer table. An answer is associated with a
    question and a submission. Make sure to use a transaction!

    :param answer: The answer value. Can be one of the following types:
                   text,
                   integer,
                   decimal,
                   date,
                   time,
                   location (given as 'LON LAT')
    :param question_id: The UUID of the question.
    :param submission_id: The UUID of the submission.
    :param survey_id: The UUID of the survey.
    :return: The Insert object. Execute this!
    """
    question = get_question(question_id)
    type_constraint_name = question.type_constraint_name
    answer_type = 'answer_' + type_constraint_name
    values = {answer_type: _sanitize_answer(answer, type_constraint_name),
              'question_id': question_id,
              'submission_id': submission_id,
              'type_constraint_name': type_constraint_name,
              'sequence_number': question.sequence_number,
              'allow_multiple': question.allow_multiple,
              'survey_id': survey_id}
    return answer_table.insert().values(values)


def get_answers(submission_id: str) -> ResultProxy:
    """
    Get all the records from the answer table identified by submission_id
    ordered by sequence number.

    :param submission_id: foreign key
    :return: an iterable of the answers (RowProxy)
    """
    select_stmt = answer_table.select()
    where_stmt = select_stmt.where(
        answer_table.c.submission_id == submission_id)
    return where_stmt.order_by('sequence_number asc').execute()


def get_geo_json(answer: RowProxy) -> str:
    """
    The default string representation of a geometry in PostGIS is some
    garbage. This function converts the garbage into a GeoJSON string that
    looks like this:
    {'coordinates': [LON, LAT], 'type': 'Point'}

    :param answer: a RowProxy object for a record in the answer table
    :return: a GeoJSON string representing the answer's value
    """
    return engine.execute(func.ST_AsGeoJSON(answer.answer_location)).scalar()
