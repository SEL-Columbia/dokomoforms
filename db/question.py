"""Allow access to the question table."""
from sqlalchemy import Table, MetaData
from sqlalchemy.engine import RowProxy, ResultProxy

from db import engine


question_table = Table('question', MetaData(bind=engine), autoload=True)


def get_question(question_id: str) -> RowProxy:
    """
    Get a record from the question table identified by question_id.

    :param question_id: primary key
    :return: the record
    """
    select_stmt = question_table.select()
    where_stmt = select_stmt.where(question_table.c.question_id == question_id)
    return where_stmt.execute().first()


def get_questions(survey_id) -> ResultProxy:
    select_stmt = question_table.select()
    where_stmt = select_stmt.where(question_table.c.survey_id == survey_id)
    return where_stmt.order_by('sequence_number asc').execute()
