"""Allow access to the question_choice table."""

from sqlalchemy.engine import RowProxy, ResultProxy, Connection
from sqlalchemy.sql import Insert, select

from dokomoforms.db import question_choice_table


def question_choice_select(connection: Connection,
                           question_choice_id: str) -> RowProxy:
    """
    Get a record from the question_choice table.

    :param question_choice_id: the UUID of the choice
    :return: the corresponding record
    :raise QuestionChoiceDoesNotExistError: if the UUID is not in the table
    """
    table = question_choice_table
    choice = connection.execute(select([table]).where(
        table.c.question_choice_id == question_choice_id)).first()
    if choice is None:
        raise QuestionChoiceDoesNotExistError(question_choice_id)
    return choice


def get_choices(connection: Connection, question_id: str) -> ResultProxy:
    """
    Get all the choices for a question identified by question_id ordered by
    choice number.

    :param connection: a SQLAlchemy Connection
    :param question_id: foreign key
    :return: an iterable of the choices (RowProxy)
    """
    select_stmt = select([question_choice_table])
    where_stmt = select_stmt.where(
        question_choice_table.c.question_id == question_id)
    return connection.execute(where_stmt.order_by('choice_number asc'))


def question_choice_insert(*,
                           question_id: str,
                           choice: str,
                           choice_number: int,
                           type_constraint_name: str,
                           question_sequence_number: int,
                           allow_multiple: bool,
                           survey_id: str) -> Insert:
    """
    Insert a record into the question_choice table. A question choice is
    associated with a question. Make sure to use a transaction!

    :param question_id: the UUID of the question
    :param choice: the text of the choice
    :param choice_number: the choice number (for ordering)
    :param type_constraint_name: type constraint
    :param question_sequence_number: sequence number
    :param allow_multiple: whether multiple answers are allowed
    :param survey_id: the UUID of the survey
    :return: the Insert object. Execute this!
    """
    values = {'question_id': question_id,
              'choice': choice,
              'choice_number': choice_number,
              'type_constraint_name': type_constraint_name,
              'question_sequence_number': question_sequence_number,
              'allow_multiple': allow_multiple,
              'survey_id': survey_id}
    return question_choice_table.insert().values(values)


class RepeatedChoiceError(Exception):
    """The same choice was supplied twice for a question."""
    pass


class QuestionChoiceDoesNotExistError(Exception):
    """The specified question choice does not exist in the database."""
    pass
