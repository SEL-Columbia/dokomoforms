"""Allow access to the question_branch table."""
from sqlalchemy import Table, MetaData
from sqlalchemy.engine import ResultProxy

from db import engine


question_branch_table = Table('question_branch', MetaData(bind=engine),
                              autoload=True)


def get_branches(question_id: str) -> ResultProxy:
    """
    Get all the branches for a question identified by question_id.

    :param question_id: foreign key
    :return: an iterable of the branches (RowProxy)
    """
    select_stmt = question_branch_table.select()
    where_stmt = select_stmt.where(
        question_branch_table.c.from_question_id == question_id)
    return where_stmt.execute()
