"""Allow access to the survey table."""
import json

from sqlalchemy import Table, MetaData
from sqlalchemy.engine import RowProxy

from db import engine
from db.question import get_questions


survey_table = Table('survey', MetaData(bind=engine), autoload=True)


def _get_fields(question: RowProxy) -> dict:
    """
    Extract the relevant fields from a record in the question table.

    :param question: A RowProxy for a record in the question table.
    :return: A dictionary of the fields.
    """
    return {'question_id': question.question_id,
            'title': question.title,
            'hint': question.hint,
            'required': question.required,
            'allow_multiple': question.allow_multiple,
            'type_constraint_name': question.type_constraint_name,
            'logical_constraint_name': question.logical_constraint_name}


def survey_json(survey_id: str) -> str:
    """
    Create a json representation of a survey.

    :param survey_id: The UUID of the survey.
    :return: A json string.
    """
    questions = get_questions(survey_id)
    questions_dict = {'survey_id': survey_id}

    # TODO: deal with question branching
    question_fields = [_get_fields(question) for question in questions]

    questions_dict['questions'] = question_fields
    return json.dumps(questions_dict)
