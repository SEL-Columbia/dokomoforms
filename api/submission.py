"""Functions for interacting with submissions."""
from heapq import merge
from collections import Iterator

from sqlalchemy.engine import ResultProxy, RowProxy

from db import engine, delete_record
from db.answer import answer_insert, get_answers, get_geo_json
from db.answer_choice import get_answer_choices
from db.submission import submission_insert, submission_select, \
    get_submissions, \
    submission_table
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

    return get(submission_id)


def _get_comparable(answers: ResultProxy) -> Iterator:
    """
    This crazy function allows records from the answer or answer_choice
    tables to be ordered by sequence number.

    :param answers: the result of a query on either the answer or answer_choice
                    table
    :return: A generator of (sequence number, RowProxy) pairs
    """
    return ((answer.sequence_number, answer) for answer in answers)


def _jsonify(answer: RowProxy, type_constraint_name: str) -> object:
    """
    This function returns a "nice" representation of an answer which can be
    serialized as JSON.

    :param answer: a record from the answer table
    :param type_constraint_name: the type constraint name
    :return: the nice representation
    """
    if type_constraint_name == 'location':
        return get_geo_json(answer)['coordinates']
    elif type_constraint_name in {'date', 'time'}:
        return answer['answer_' + type_constraint_name].isoformat()
    else:
        return answer['answer_' + type_constraint_name]


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
        answer_field = _jsonify(answer, type_constraint_name)
    # TODO: determine which fields to return
    return {'answer_id': answer.answer_id,
            'question_id': answer.question_id,
            'type_constraint_name': type_constraint_name,
            'answer': answer_field}


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
                    'survey_id': submission.survey_id,
                    'submitter': submission.submitter,
                    'submission_time': submission.submission_time.isoformat(),
                    'answers': [_get_fields(answer) for num, answer in result]}
    return answers_dict


def get_for_survey(survey_id: str) -> dict:
    """
    Create a JSON representation of the submissions to a given survey.

    :param survey_id: the UUID of the survey
    :return: a JSON dict
    """
    submissions = get_submissions(survey_id)
    return [get(sub.submission_id) for sub in submissions]


def delete(submission_id: str):
    """
    Delete the submission specified by the given submission_id

    :param submission_id: the UUID of the submission
    """
    with engine.connect() as connection:
        connection.execute(
            delete_record(submission_table, 'submission_id', submission_id))
    return {'message': 'Submission deleted'}
