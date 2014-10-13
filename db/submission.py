"""Allow access to the submission table."""
from _ast import Tuple
from collections import Iterator
from heapq import merge
import json

from sqlalchemy import Table, MetaData
from sqlalchemy.engine import ResultProxy, RowProxy
from sqlalchemy.sql.dml import Insert

from db import engine
from db.answer import get_answers
from db.answer_choice import get_answer_choices
from db.question import get_question


submission_table = Table('submission', MetaData(bind=engine), autoload=True)


def submission_insert(*, latitude: float, longitude: float, submitter: str,
                      survey_id: str) -> Insert:
    """
    Insert a record into the submission table.

    :param latitude: degrees
    :param longitude: degrees
    :param submitter: name
    :param survey_id: The UUID of the survey.
    :return: The Insert object. Execute this!
    """
    values = {'latitude': latitude,
              'longitude': longitude,
              'submitter': submitter,
              'survey_id': survey_id}
    return submission_table.insert().values(values)


def _get_comparable(answers: ResultProxy) -> Iterator[Tuple[int, RowProxy]]:
    """
    This crazy function allows records from the answer or answer_choice
    tables to be ordered by sequence number.

    :param answers: the result of a query on either the answer or answer_choice
                    table
    :return: A generator of (sequence number, RowProxy) pairs
    """
    return ((answer.sequence_number, answer) for answer in answers)


def _get_fields(answer: RowProxy) -> dict:
    """
    Extract the relevant fields for an answer (from the answer or
    answer_choice table).

    :param answer: A record in the answer or answer_choice table
    :return: A dictionary of the fields.
    """
    question = get_question(answer.question_id)
    try:
        # Get the choice for a multiple choice question
        answer_field = answer.question_choice_id
    except AttributeError:
        # The answer is not a choice
        type_constraint_name = answer.type_constraint_name
        if type_constraint_name == 'multiple_choice_with_other':
            type_constraint_name = 'text'
        answer_field = answer['answer_' + type_constraint_name]
    # TODO: determine which fields to return
    return {'question_id': answer.question_id,
            'title': question.title,
            'answer': answer_field,
            'answer_type': type_constraint_name}


def submission_json(submission_id: str) -> str:
    """
    Create a json representation of a submission.

    :param submission_id: primary key
    :return: a json string
    """
    answers = _get_comparable(get_answers(submission_id))
    choices = _get_comparable(get_answer_choices(submission_id))
    # The merge is necessary to get the answers in sequence number order.
    result = merge(answers, choices)
    answers_dict = {'submission_id': submission_id,
                    'answers': [_get_fields(answer) for num, answer in result]}
    return json.dumps(answers_dict)
