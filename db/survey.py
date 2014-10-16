"""Allow access to the survey table."""
import json

from sqlalchemy import Table, MetaData
from sqlalchemy.engine import RowProxy
from sqlalchemy.sql import Insert

from db import engine
from db.auth_user import auth_user_table
from db.question import get_questions
from db.question_branch import get_branches
from db.question_choice import get_choices


survey_table = Table('survey', MetaData(bind=engine), autoload=True)

# TODO: more than one user
AUTH_USER_ID = auth_user_table.select().execute().first().auth_user_id


# TODO: remove hardcoded user
def survey_insert(*, auth_user_id=AUTH_USER_ID, title: str) -> Insert:
    """
    Insert a record into the survey table.

    :param auth_user_id: The UUID of the user.
    :param title: The survey's title
    :return: The Insert object. Execute this!
    """
    return survey_table.insert().values(title=title, auth_user_id=auth_user_id)


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


def survey_json(survey_id: str) -> str:
    """
    Create a json representation of a survey.

    :param survey_id: The UUID of the survey.
    :return: A json string.
    """
    questions = get_questions(survey_id)
    questions_dict = {'survey_id': survey_id}

    question_fields = [_get_fields(question) for question in questions]

    questions_dict['questions'] = question_fields
    return json.dumps(questions_dict)
