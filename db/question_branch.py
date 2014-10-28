"""Allow access to the question_branch table."""
from sqlalchemy import Table, MetaData
from sqlalchemy.engine import ResultProxy
from sqlalchemy.sql import Insert

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


def question_branch_insert(*,
                           question_choice_id: str,
                           from_question_id: str,
                           from_type_constraint: str,
                           from_sequence_number: str,
                           from_allow_multiple: str,
                           from_survey_id: str,
                           to_question_id: str,
                           to_type_constraint: str,
                           to_sequence_number: str,
                           to_allow_multiple: str,
                           to_survey_id: str) -> Insert:
    """
    Insert a record into the question_branch table. A question branch is
    associated with a choice associated with a question (the from question)
    and another question (the to question). Make sure to use a transaction!

    :param question_choice_id: the UUID of the choice
    :param from_question_id: the UUID of the from question
    :param from_type_constraint: the type constraint of the from question
    :param from_sequence_number: the sequence number of the from question
    :param from_allow_multiple: whether the from question allows multiple
    :param from_survey_id: the UUID of the survey of the from question
    :param to_question_id: the UUID of the to question
    :param to_type_constraint: the type constraint of the to question
    :param to_sequence_number: the sequence number of the to question
    :param to_allow_multiple: whether the to question allows multiple
    :param to_survey_id: the UUID of the survey of the to question
    :return: an Insert object. Execute this!
    """
    values = {'question_choice_id': question_choice_id,
              'from_question_id': from_question_id,
              'from_type_constraint': from_type_constraint,
              'from_sequence_number': from_sequence_number,
              'from_allow_multiple': from_allow_multiple,
              'from_survey_id': from_survey_id,
              'to_question_id': to_question_id,
              'to_type_constraint': to_type_constraint,
              'to_sequence_number': to_sequence_number,
              'to_allow_multiple': to_allow_multiple,
              'to_survey_id': to_survey_id}
    return question_branch_table.insert().values(values)
