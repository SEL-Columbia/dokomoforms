"""Functions for interacting with submissions."""
from heapq import merge
from collections import Iterator

from sqlalchemy.engine import ResultProxy, RowProxy

from db import engine
from db.answer import answer_insert, get_answers
from db.answer_choice import get_answer_choices
from db.submission import submission_insert, submission_select, get_submissions
from db.question import get_question


def submit(data: dict) -> dict:
    """
    Create a submission with answers.

    :param data: representation of the submission (from json.loads)
    :return: the UUID of the submission in the database
    """
    submission_id = None

    survey_id = data['survey_id']
    all_answers = data['answers']
    # Filter out the skipped questions in the submission.
    answers = (ans for ans in all_answers if ans['answer'] is not None)

    with engine.begin() as connection:
        submission_values = {'submitter': '',
                             'survey_id': survey_id}
        result = connection.execute(submission_insert(**submission_values))
        submission_id = result.inserted_primary_key[0]

        for answer_dict in answers:
            # TODO: Deal with multiple choice
            # Add a few fields to the answer_dict
            value_dict = answer_dict.copy()
            value_dict['submission_id'] = submission_id
            value_dict['survey_id'] = survey_id
            connection.execute(answer_insert(**value_dict))

    return {'submission_id': submission_id}


def _get_comparable(answers: ResultProxy) -> Iterator:
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
            'type_constraint_name': type_constraint_name}


# TODO: Figure out if this function should take a survey_id as a parameter
def get(submission_id: str) -> dict:
    """
    Create a JSON representation of a submission.

    :param submission_id: the UUID of the submission
    :return: a JSON dict
    """
    submission = submission_select(submission_id)
    answers = _get_comparable(get_answers(submission_id))
    choices = _get_comparable(get_answer_choices(submission_id))
    # The merge is necessary to get the answers in sequence number order.
    result = merge(answers, choices)
    answers_dict = {'submission_id': submission_id,
                    'submitter': submission.submitter,
                    'submission_time': submission.submission_time,
                    'answers': [_get_fields(answer) for num, answer in result]}
    return answers_dict


def get_for_survey(survey_id: str) -> dict:
    """
    Create a JSON representation of the submissions to a given survey.

    :param survey_id: the UUID of the survey
    :return: a JSON dict
    """
    submissions = get_submissions(survey_id)
    return {'survey_id': survey_id,
            'submissions': [get(sub.submission_id) for sub in submissions]}
