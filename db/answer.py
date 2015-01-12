"""Allow access to the answer table."""
import json
from sqlalchemy import Table, MetaData, text

from sqlalchemy.engine import ResultProxy, RowProxy
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql import func
from tornado.escape import json_decode

from db import engine
from db.question import question_select


answer_table = Table('answer', MetaData(bind=engine), autoload=True)


def _sanitize_answer(answer, type_constraint_name: str) -> str:
    """
    Certain question types require some massaging in order to go into the
    database properly. This function does that massaging.

    location: uses the ST_GeomFromText function in the database. The input
    must be in the form [LON, LAT]. Uses SRID 4326 (AKA WGS 84
    http://en.wikipedia.org/wiki/World_Geodetic_System), which should work with
    the coordinates given by Android phones.

    :param answer: The answer value.
    :param type_constraint_name: The type constraint for the question
    :return: The answer in a form that is insertable
    """
    if type_constraint_name == 'location':
        if answer is None:
            return text("ST_GeomFromText('POINT EMPTY', 4326)")
        else:
            db_input = "ST_GeomFromText('POINT({ans[0]} {ans[1]})', 4326)"
            return text(db_input.format(ans=answer))
    return answer


def answer_insert(*,
                  answer,
                  question_id: str,
                  submission_id: str,
                  type_constraint_name: str,
                  sequence_number: int,
                  allow_multiple: bool,
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
                   location (given as [LON, LAT])
    :param question_id: The UUID of the question.
    :param submission_id: The UUID of the submission.
    :param type_constraint_name: the type constraint
    :param sequence_number: the sequence number
    :param allow_multiple: whether there can be multiple answers
    :param survey_id: The UUID of the survey.
    :return: The Insert object. Execute this!
    """
    question = question_select(question_id)
    other = question.logic['with_other']
    answer_type = 'answer_text' if other else 'answer_' + type_constraint_name
    values = {answer_type: _sanitize_answer(answer, type_constraint_name),
              'question_id': question_id,
              'submission_id': submission_id,
              'type_constraint_name': type_constraint_name,
              'sequence_number': sequence_number,
              'allow_multiple': allow_multiple,
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


def get_answers_for_question(question_id: str) -> ResultProxy:
    """
    Get all the records from the answer table identified by question_id.

    :param question_id: foreign key
    :return: an iterable of the answers (RowProxy)
    """
    select_stmt = answer_table.select()
    where_stmt = select_stmt.where(answer_table.c.question_id == question_id)
    return where_stmt.execute()


def get_geo_json(answer: RowProxy) -> dict:
    """
    The default string representation of a geometry in PostGIS is some
    garbage. This function returns, instead of garbage, a GeoJSON dict that
    looks like this:
    {'coordinates': [LON, LAT], 'type': 'Point'}

    UNLESS of course the point in question is empty, in which case it looks
    like this:
    {'coordinates': [], 'type': 'MultiPoint'}

    :param answer: a RowProxy object for a record in the answer table
    :return: a GeoJSON dict representing the answer's value
    """
    result = engine.execute(func.ST_AsGeoJSON(answer.answer_location)).scalar()
    return json_decode(result)


class CannotAnswerMultipleTimesError(Exception):
    """A submission contains multiple answers to a question with
    allow_multiple == False."""
    pass
