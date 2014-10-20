"""Functions for interacting with surveys."""
import json

from sqlalchemy.engine import RowProxy

from db import engine
from db.question import question_insert, get_questions
from db.question_branch import get_branches
from db.question_choice import get_choices
from db.survey import survey_insert


def create(data: str) -> str:
    """
    Create a survey with questions.

    :param data: a representation of the survey (from json.loads)
    :return: the UUID of the survey in the database
    """
    survey_id = None

    # user_id = json_data['auth_user_id']
    title = data['title']
    questions = data['questions']

    with engine.begin() as connection:
        survey_values = {  # 'auth_user_id': user_id,
                           'title': title}
        result = connection.execute(survey_insert(**survey_values))
        survey_id = result.inserted_primary_key[0]

        for question_dict in questions:
            # Add fields to the question_dict
            values_dict = question_dict.copy()
            values_dict['survey_id'] = survey_id
            q_exec = connection.execute(question_insert(**values_dict))
            question_id = q_exec.inserted_primary_key[0]
            if 'choices' in question_dict:
                # TODO: multiple_choice questions
                if 'branches' in question_dict:
                    # TODO: branching
                    pass

    return survey_id


def _get_choice_fields(choice: RowProxy) -> dict:
    """
    Extract the relevant fields from a record in the question_choice table.

    :param choice: A RowProxy for a record in the question_choice table.
    :return: A dictionary of the fields.
    """
    return {'question_choice_id': choice.question_choice_id,
            'choice': choice.choice,
            'choice_number': choice.choice_number}


def _get_branch_fields(branch: RowProxy) -> dict:
    """
    Extract the relevant fields from a record in the question_branch table.

    :param branch: A RowProxy for a record in the question_branch table.
    :return: A dictionary of the fields.
    """
    return {'question_choice_id': branch.question_choice_id,
            'to_question_id': branch.to_question_id}


def _get_fields(question: RowProxy) -> dict:
    """
    Extract the relevant fields from a record in the question table.

    :param question: A RowProxy for a record in the question table.
    :return: A dictionary of the fields.
    """
    result = {'question_id': question.question_id,
              'title': question.title,
              'hint': question.hint,
              'required': question.required,
              'sequence_number': question.sequence_number,
              'allow_multiple': question.allow_multiple,
              'type_constraint_name': question.type_constraint_name,
              'logical_constraint_name': question.logical_constraint_name}
    if question.type_constraint_name.startswith('multiple_choice'):
        choices = get_choices(question.question_id)
        result['choices'] = [_get_choice_fields(choice) for choice in choices]
        branches = get_branches(question.question_id)
        if branches.rowcount > 0:
            result['branches'] = [_get_branch_fields(brn) for brn in branches]
    return result


def get(data: str) -> str:
    """
    Get a JSON representation of a survey.

    :param data: JSON containing the UUID of the survey.
    :return: The JSON string representation.
    """
    questions = get_questions(data['survey_id'])
    questions_dict = {'survey_id': data['survey_id']}

    question_fields = [_get_fields(question) for question in questions]

    questions_dict['questions'] = question_fields
    return json.dumps(questions_dict)
