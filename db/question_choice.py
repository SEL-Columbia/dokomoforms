"""Allow access to the question_choice table."""
from sqlalchemy import Table, MetaData
from sqlalchemy.engine import RowProxy, ResultProxy

from db import engine


question_choice_table = Table('question_choice', MetaData(bind=engine),
                              autoload=True)


def get_choices(question_id: str) -> ResultProxy:
    """
    Get all the choices for a question identified by question_id ordered by
    choice number.

    :param question_id: foreign key
    :return: an iterable of the choices (RowProxy)
    """
    select_stmt = question_choice_table.select()
    where_stmt = select_stmt.where(
        question_choice_table.c.question_id == question_id)
    return where_stmt.order_by('choice_number asc').execute()
