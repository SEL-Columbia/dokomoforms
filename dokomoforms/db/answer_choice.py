"""Allow access to the answer_choice table."""
from sqlalchemy import select
from sqlalchemy.engine import ResultProxy, Connection
from sqlalchemy.sql.dml import Insert

from dokomoforms.db import answer_choice_table


def answer_choice_insert(*,
                         is_other: bool=None,
                         question_choice_id: str,
                         question_id: str,
                         submission_id: str,
                         type_constraint_name: str,
                         sequence_number: int,
                         allow_multiple: bool,
                         survey_id: str) -> Insert:
    """
    Insert a record into the answer_choice table. An answer choice is
    associated with a question, a question choice, and a submission. Make
    sure to use a transaction!

    :param is_other: may be passed in for convenience, but is unused
    :param question_choice_id: The answer value. References the
                               question_choice table.
    :param question_id: The UUID of the question.
    :param submission_id: The UUID of the submission.
    :param type_constraint_name: the type constraint
    :param sequence_number: the sequence number
    :param allow_multiple: whether multiple answers are allowed
    :param survey_id: The UUID of the survey.
    :return: The Insert object. Execute this!
    """
    values = {'question_choice_id': question_choice_id,
              'question_id': question_id,
              'submission_id': submission_id,
              'type_constraint_name': type_constraint_name,
              'sequence_number': sequence_number,
              'allow_multiple': allow_multiple,
              'survey_id': survey_id}
    return answer_choice_table.insert().values(values)


def get_answer_choices(connection: Connection,
                       submission_id: str) -> ResultProxy:
    """
    Get all the records from the answer_choice table identified by
    submission_id ordered by sequence number.

    :param connection: a SQLAlchemy Connection
    :param submission_id: foreign key
    :return: an iterable of the answer choices (RowProxy)
    """
    select_stmt = select([answer_choice_table])
    where_stmt = select_stmt.where(
        answer_choice_table.c.submission_id == submission_id)
    return connection.execute(where_stmt.order_by('sequence_number asc'))


def get_answer_choices_for_choice_id(connection: Connection,
                                     question_choice_id: str) -> ResultProxy:
    """
    Get all the records from the answer_choice table identified by
    question_choice_id.

    :param connection: a SQLAlchemy Connection
    :param question_choice_id: foreign key
    :return: an iterable of the answer choices (RowProxy)
    """
    select_stmt = select([answer_choice_table])
    where_stmt = select_stmt.where(
        answer_choice_table.c.question_choice_id == question_choice_id)
    return connection.execute(where_stmt)
