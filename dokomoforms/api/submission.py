"""Functions for interacting with submissions."""
from heapq import merge
from collections import Iterator

from sqlalchemy.engine import ResultProxy, RowProxy, Connection
from sqlalchemy.sql import Insert

from dokomoforms.api import execute_with_exceptions, json_response
from dokomoforms.db import delete_record, submission_table
from dokomoforms.db.answer import answer_insert, get_answers, get_geo_json, \
    CannotAnswerMultipleTimesError, _get_is_other
from dokomoforms.db.answer_choice import get_answer_choices, \
    answer_choice_insert
from dokomoforms.db.question import question_select, get_required
from dokomoforms.db.question_choice import question_choice_select
from dokomoforms.db.submission import submission_insert, submission_select, \
    get_submissions_by_email
from dokomoforms.db.survey import SurveyDoesNotExistError, get_email_address, \
    IncorrectQuestionIdError


class RequiredQuestionSkippedError(Exception):
    """A submission does not contain an answer to a required question."""
    pass


def _insert_answer(connection: Connection,
                   answer: dict,
                   submission_id: str,
                   survey_id: str) -> Insert:
    """
    Insert an answer from a submission into either the answer or
    answer_choice table. Don't forget to use a transaction!

    :param connection: a SQLAlchemy Connection
    :param answer: a dictionary of the answer values
    :param submission_id: the UUID of the submission
    :param survey_id: the UUID of the survey
    :return: the Insert object. Execute this!
    """
    # Add a few fields to the answer dict
    value_dict = answer.copy()
    value_dict['submission_id'] = submission_id
    value_dict['survey_id'] = survey_id
    question = question_select(connection, value_dict['question_id'])
    value_dict['type_constraint_name'] = question.type_constraint_name
    value_dict['sequence_number'] = question.sequence_number
    value_dict['allow_multiple'] = question.allow_multiple
    # determine whether this is a choice selection
    is_mc = question.type_constraint_name == 'multiple_choice'
    is_other = value_dict.get('is_other')
    if is_mc and not is_other:
        value_dict['question_choice_id'] = value_dict.pop('answer')
        # Might want to change 'answer_choice_metadata' to 'answer_metadata'...
        answer_metadata = value_dict.pop('answer_metadata')
        value_dict['answer_choice_metadata'] = answer_metadata
        insert = answer_choice_insert
    else:
        insert = answer_insert
    return insert(**value_dict)


def _answer_not_none(answer: dict) -> bool:
    """
    Return whether the "answer" value is None

    :param answer: the dict containing the answer value
    :return: whether it is None
    """
    return answer['answer'] is not None


def _create_submission(connection: Connection,
                       survey_id: str,
                       required_ids: set,
                       submission_data: dict) -> str:
    """
    Create a submission to the specified survey with the given submission
    data and return the submission id.

    :param connection: a SQLAlchemy Connection
    :param survey_id: the UUID of the survey
    :param required_ids: a set of UUIDs for questions which are marked
                         "required"
    :param submission_data: the dict containing the submission information
    :return: the id of the submission
    :raise RequiredQuestionSkippedError: if a "required" question has no answer
    """
    unanswered_required = required_ids.copy()
    submitter = submission_data['submitter']
    all_answers = submission_data['answers']
    answers = filter(_answer_not_none, all_answers)

    submission_values = {
        'submitter': submitter, 'survey_id': survey_id
    }
    executable = submission_insert(**submission_values)
    exceptions = [
        ('submission_survey_id_fkey',
         SurveyDoesNotExistError(survey_id))
    ]
    result = execute_with_exceptions(
        connection, executable, exceptions)
    submission_id = result.inserted_primary_key[0]

    for answer in answers:
        executable = _insert_answer(
            connection, answer, submission_id, survey_id)
        exceptions = [
            ('only_one_answer_allowed',
             CannotAnswerMultipleTimesError(answer['question_id'])),
            ('answer_question_id_fkey',
             IncorrectQuestionIdError(answer['question_id']))
        ]
        execute_with_exceptions(connection, executable, exceptions)
        unanswered_required.discard(answer['question_id'])

    if unanswered_required:
        raise RequiredQuestionSkippedError(unanswered_required)

    return submission_id


def submit(connection: Connection, data: dict) -> dict:
    """
    Create a submission with answers.

    :param connection: a SQLAlchemy connection
    :param data: representation of the submission (from json.loads)
    :return: the UUID of the submission in the database
    :raise RequiredQuestionSkipped: if there is no answer for a required
                                    question
    """
    c = connection
    survey_id = data['survey_id']
    required = {q.question_id for q in
                get_required(connection, survey_id)}

    with c.begin():
        submission_id = _create_submission(c, survey_id, required, data)

    email = get_email_address(connection, survey_id)
    return get_one(c, submission_id, email=email)


def _get_comparable(answers: ResultProxy) -> Iterator:
    """
    This crazy function allows records from the answer or answer_choice
    tables to be ordered by sequence number.

    :param answers: the result of a query on either the answer or answer_choice
                    table
    :return: A generator of (sequence number, RowProxy) pairs
    """
    return ((answer.sequence_number, answer) for answer in answers)


def _jsonify(connection: Connection,
             answer: RowProxy,
             type_constraint_name: str) -> object:
    """
    This function returns a "nice" representation of an answer which can be
    serialized as JSON.

    :param connection: a SQLAlchemy Connection
    :param answer: a record from the answer table
    :param type_constraint_name: the type constraint name
    :return: the nice representation
    """
    if type_constraint_name in {'location', 'facility'}:
        return get_geo_json(connection, answer)['coordinates']
    elif type_constraint_name in {'date', 'time'}:
        return answer['answer_' + type_constraint_name].isoformat()
    elif type_constraint_name == 'decimal':
        return float(answer['answer_' + type_constraint_name])
    else:
        return answer['answer_' + type_constraint_name]


def _get_fields(connection: Connection, answer: RowProxy) -> dict:
    """
    Extract the relevant fields for an answer (from the answer or
    answer_choice table).

    :param connection: a SQLAlchemy connection
    :param answer: A record in the answer or answer_choice table
    :return: A dictionary of the fields.
    """
    tcn = answer.type_constraint_name
    question_id = answer.question_id
    question = question_select(connection, question_id)
    result_dict = {'question_id': question_id,
                   'question_title': question.question_title,
                   'sequence_number': question.sequence_number,
                   'type_constraint_name': tcn,
                   'is_other': _get_is_other(answer)}
    try:
        # Get the choice for a multiple choice question
        choice_id = answer.question_choice_id
        result_dict['answer'] = choice_id
        result_dict['answer_id'] = answer.answer_choice_id

        choice = question_choice_select(connection, choice_id)
        result_dict['choice'] = choice.choice
        result_dict['choice_number'] = choice.choice_number
    except AttributeError:
        # The answer is not a choice
        question = question_select(connection, answer.question_id)
        if answer.is_other:
            tcn = 'text'
        result_dict['answer'] = _jsonify(connection, answer, tcn)
        result_dict['answer_id'] = answer.answer_id
        result_dict['choice'] = None
        result_dict['choice_number'] = None
    return result_dict


def get_one(connection: Connection, submission_id: str, email: str) -> dict:
    """
    Create a JSON representation of a submission.

    :param connection: a SQLAlchemy Connection
    :param submission_id: the UUID of the submission
    :param email: the user's e-mail address
    :return: a JSON dict
    """
    submission = submission_select(connection, submission_id, email=email)
    answers = _get_comparable(get_answers(connection, submission_id))
    choices = _get_comparable(get_answer_choices(connection, submission_id))
    # The merge is necessary to get the answers in sequence number order.
    result = merge(answers, choices)
    c = connection
    sub_dict = {'submission_id': submission_id,
                'survey_id': submission.survey_id,
                'submitter': submission.submitter,
                'submission_time': submission.submission_time.isoformat(),
                'answers': [_get_fields(c, answer) for num, answer in result]}
    return json_response(sub_dict)


def get_all(connection: Connection,
            survey_id: str,
            email: str,
            submitters: Iterator=None,
            filters: list=None) -> dict:
    """
    Create a JSON representation of the submissions to a given survey and
    email.

    :param connection: a SQLAlchemy Connection
    :param survey_id: the UUID of the survey
    :param email: the user's e-mail address
    :param submitters: if supplied, filters results by all given submitters
    :param filters: if supplied, filters results by answers
    :return: a JSON dict
    """
    submissions = get_submissions_by_email(connection,
                                           survey_id,
                                           email=email,
                                           submitters=submitters,
                                           filters=filters)
    # TODO: Check if this is a performance problem
    result = [get_one(connection,
                      sub.submission_id,
                      email=email) for sub in submissions]
    return json_response(result)


def delete(connection: Connection, submission_id: str):
    """
    Delete the submission specified by the given submission_id

    :param connection: a SQLAlchemy Connection
    :param submission_id: the UUID of the submission
    """
    with connection.begin():
        connection.execute(
            delete_record(submission_table, 'submission_id', submission_id))
    return json_response('Submission deleted')
