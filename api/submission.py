"""Functions for interacting with submissions."""
from heapq import merge
from collections import Iterator

from sqlalchemy.engine import ResultProxy, RowProxy
from sqlalchemy.sql import Insert

from api import execute_with_exceptions
from db import engine, delete_record
from db.answer import answer_insert, get_answers, get_geo_json, \
    CannotAnswerMultipleTimes
from db.answer_choice import get_answer_choices, answer_choice_insert
from db.question import question_select
from db.question_choice import question_choice_select
from db.submission import submission_insert, submission_select, \
    get_submissions, submission_table
from db.survey import SurveyDoesNotExistError


def _filter_skipped_questions(answers: list) -> Iterator:
    """
    Given a list of dictionaries that could look like {'answer': ...} or {
    'question_choice_id': ...}, yield the dictionaries that contain a
    not-None value.

    :param answers: a list of JSON dictionaries containing answers
    :return: an iterable of the dictionaries that contain answers
    """
    for answer in answers:
        answer_value = answer.get('answer', None)
        choice_value = answer.get('question_choice_id', None)
        if (answer_value is not None) or (choice_value is not None):
            yield answer


def _insert_answer(answer: dict, submission_id: str, survey_id: str) -> Insert:
    """
    Insert an answer from a submission into either the answer or
    answer_choice table. Don't forget to use a transaction!

    :param answer: a dictionary of the answer values
    :param submission_id: the UUID of the submission
    :param survey_id: the UUID of the survey
    :return: the Insert object. Execute this!
    """
    # Add a few fields to the answer dict
    value_dict = answer.copy()
    value_dict['submission_id'] = submission_id
    value_dict['survey_id'] = survey_id
    question = question_select(value_dict['question_id'])
    value_dict['type_constraint_name'] = question.type_constraint_name
    value_dict['sequence_number'] = question.sequence_number
    value_dict['allow_multiple'] = question.allow_multiple
    # determine whether this is a choice selection
    is_choice = 'question_choice_id' in value_dict
    insert = answer_choice_insert if is_choice else answer_insert
    return insert(**value_dict)


def submit(data: dict) -> dict:
    """
    Create a submission with answers.

    :param data: representation of the submission (from json.loads)
    :return: the UUID of the submission in the database
    """
    survey_id = data['survey_id']
    all_answers = data['answers']
    answers = _filter_skipped_questions(all_answers)

    with engine.begin() as connection:
        submission_values = {'submitter': '',
                             'survey_id': survey_id}
        executable = submission_insert(**submission_values)
        exceptions = [
            ('submission_survey_id_fkey', SurveyDoesNotExistError(survey_id))]
        result = execute_with_exceptions(connection, executable, exceptions)
        submission_id = result.inserted_primary_key[0]

        for answer in answers:
            executable = _insert_answer(answer, submission_id, survey_id)
            exceptions = [('only_one_answer_allowed',
                           CannotAnswerMultipleTimes(answer['question_id']))]
            execute_with_exceptions(connection, executable, exceptions)

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
    elif type_constraint_name == 'decimal':
        return float(answer['answer_' + type_constraint_name])
    else:
        return answer['answer_' + type_constraint_name]


def _get_fields(answer: RowProxy) -> dict:
    """
    Extract the relevant fields for an answer (from the answer or
    answer_choice table).

    :param answer: A record in the answer or answer_choice table
    :return: A dictionary of the fields.
    """
    result_dict = {'question_id': answer.question_id,
                   'type_constraint_name': answer.type_constraint_name}
    tcn = answer.type_constraint_name
    try:
        # Get the choice for a multiple choice question
        choice_id = answer.question_choice_id
        result_dict['question_choice_id'] = choice_id
        result_dict['answer_id'] = answer.answer_choice_id

        choice = question_choice_select(choice_id)
        result_dict['choice'] = choice.choice
        result_dict['choice_number'] = choice.choice_number
    except AttributeError:
        # The answer is not a choice
        if tcn == 'multiple_choice_with_other':
            tcn = 'text'
        result_dict['answer'] = _jsonify(answer, tcn)
        result_dict['answer_id'] = answer.answer_id
    return result_dict


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
    sub_dict = {'submission_id': submission_id,
                'survey_id': submission.survey_id,
                'submitter': submission.submitter,
                'submission_time': submission.submission_time.isoformat(),
                'answers': [_get_fields(answer) for num, answer in result]}
    return sub_dict


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
