"""Functions for interacting with surveys."""

from sqlalchemy.engine import RowProxy

from db import engine, update_record
from db.logical_constraint import logical_constraint_name_insert, \
    logical_constraint_exists
from db.question import question_insert, get_questions, question_table
from db.question_branch import get_branches
from db.question_choice import get_choices
from db.survey import survey_insert, survey_select, survey_table


def create(data: dict) -> dict:
    """
    Create a survey with questions.

    :param data: a JSON representation of the survey
    :return: the UUID of the survey in the database
    """
    survey_id = None

    # user_id = json_data['auth_user_id']
    title = data['title']
    questions = data.get('questions', None)

    with engine.begin() as connection:
        survey_values = {  # 'auth_user_id': user_id,
                           'title': title}
        result = connection.execute(survey_insert(**survey_values))
        survey_id = result.inserted_primary_key[0]

        for question_dict in questions:
            # Add fields to the question_dict
            values_dict = question_dict.copy()
            values_dict['survey_id'] = survey_id
            lcn = values_dict['logical_constraint_name']
            if lcn is not None and not logical_constraint_exists(lcn):
                connection.execute(logical_constraint_name_insert(lcn))
            q_exec = connection.execute(question_insert(**values_dict))
            question_id = q_exec.inserted_primary_key[0]
            if 'choices' in question_dict:
                # TODO: multiple_choice questions
                if 'branches' in question_dict:
                    # TODO: branching
                    pass

    return {'survey_id': survey_id}


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


def _to_json(survey: RowProxy) -> dict:
    """
    Return the JSON representation of the given survey

    :param survey: the survey object
    :return: a JSON dict representation
    """
    questions = get_questions(survey.survey_id)
    question_fields = [_get_fields(question) for question in questions]
    return {'survey_id': survey.survey_id,
            'title': survey.title,
            'questions': question_fields}


def get_one(data: dict) -> dict:
    """
    Get a JSON representation of a survey.

    :param data: JSON containing the UUID of the survey
    :return: the JSON representation.
    """
    survey = survey_select(data['survey_id'])
    return _to_json(survey)


# TODO: restrict this by user
# def get_many(data: dict) -> dict:
def get_many() -> dict:
    """
    Return a JSON representation of all the surveys. In the future this will
    be on a per-user basis.

    :return: the JSON string representation
    """
    surveys = survey_table.select().execute()
    return [_to_json(survey) for survey in surveys]


# TODO: look into refactoring this
def update(data: dict):
    """
    Update a survey (title, questions). You can also add questions here.

    :param data: JSON containing the UUID of the survey and fields to update.
    """
    survey_id = data['survey_id']

    with engine.connect() as connection:
        if 'title' in data:
            values = {'title': data['title']}
            s_upd = update_record(survey_table, 'survey_id', survey_id, values)
            connection.execute(s_upd)
        for question_dict in data.get('questions', None):
            values_dict = question_dict.copy()
            if 'question_id' in question_dict:
                # update existing question
                q_id = values_dict.pop('question_id')
                choices = values_dict.pop('choices', None)
                branches = values_dict.pop('branches', None)
                q_upd = update_record(question_table, 'question_id', q_id,
                                      values_dict)
                connection.execute(q_upd)
                if choices:
                    # TODO: choices update or insert
                    if branches:
                        pass
                        # TODO: branches update or insert
            else:
                # create new question
                values_dict['survey_id'] = survey_id
                lcn = values_dict['logical_constraint_name']
                if lcn is not None and not logical_constraint_exists(lcn):
                    connection.execute(logical_constraint_name_insert(lcn))
                q_exec = connection.execute(question_insert(**values_dict))
                question_id = q_exec.inserted_primary_key[0]
                if 'choices' in question_dict:
                    # TODO: multiple_choice questions
                    if 'branches' in question_dict:
                        # TODO: branching
                        pass


