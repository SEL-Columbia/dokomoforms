"""Functions for interacting with surveys."""

from sqlalchemy.engine import RowProxy

from db import engine, update_record, delete_record
from db.question import question_insert, get_questions, question_table, \
    get_free_sequence_number, question_select
from db.question_branch import get_branches
from db.question_choice import get_choices, question_choice_insert, \
    question_choice_table
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
    questions = data.get('questions', [])

    with engine.begin() as connection:
        # First, create an entry in the survey table
        survey_values = {  # 'auth_user_id': user_id,
                           'title': title}
        result = connection.execute(survey_insert(**survey_values))
        survey_id = result.inserted_primary_key[0]

        # Now insert questions. We need to do some trickery with the
        # sequence numbers.
        cur_sequence_number = 1
        for question_dict in questions:
            # Add fields to the question_dict
            values_dict = question_dict.copy()
            sequence_number = values_dict['sequence_number']
            if sequence_number is None:
                values_dict['sequence_number'] = cur_sequence_number
                cur_sequence_number += 1
            values_dict['survey_id'] = survey_id
            q_exec = connection.execute(question_insert(**values_dict))
            question_id = q_exec.inserted_primary_key[0]

            # Having inserted the question, we need to insert the choices (
            # if there are any)
            enum = enumerate(values_dict.get('choices', []), start=1)
            for number, choice in enum:
                tcn = values_dict['type_constraint_name']
                seq = values_dict['sequence_number']
                mul = values_dict['allow_multiple']
                if mul is None:
                    mul = False
                choice_dict = {'question_id': question_id,
                               'survey_id': survey_id,
                               'choice': choice,
                               'choice_number': number,
                               'type_constraint_name': tcn,
                               'question_sequence_number': seq,
                               'allow_multiple': mul}
                connection.execute(question_choice_insert(**choice_dict))
                if 'branches' in values_dict:
                    # TODO: branching
                    pass

    return get_one(survey_id)


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
              'logic': question.logic}
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


def get_one(survey_id: str) -> dict:
    """
    Get a JSON representation of a survey.

    :param data: JSON containing the UUID of the survey
    :return: the JSON representation.
    """
    survey = survey_select(survey_id)
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
    cur_sequence_number = get_free_sequence_number(survey_id)

    with engine.connect() as connection:
        if 'title' in data:
            values = {'title': data['title']}
            s_upd = update_record(survey_table, 'survey_id', survey_id, values)
            connection.execute(s_upd)

        for question_dict in data.get('questions', []):
            values_dict = question_dict.copy()
            if 'question_id' in question_dict:
                # update existing question
                q_id = values_dict.pop('question_id')
                choices = values_dict.pop('choices', [])
                branches = values_dict.pop('branches', [])
                q_upd = update_record(question_table, 'question_id', q_id,
                                      values_dict)
                connection.execute(q_upd)
                if choices:
                    # delete the existing choices and replace them with the
                    # new ones
                    for ch_id in list(get_choices(q_id)):
                        tbl = question_choice_table
                        d_ch = delete_record(tbl, 'question_choice_id', ch_id)
                        connection.execute(d_ch)
                    for number, choice in enumerate(choices, start=1):
                        choice_dict = {'question_id': q_id,
                                       'survey_id': survey_id,
                                       'choice': choice,
                                       'choice_number': number}
                    connection.execute(question_choice_insert(**choice_dict))
                    if branches:
                        pass
                        # TODO: branches update or insert
            else:
                # create new question
                values_dict['survey_id'] = survey_id
                if values_dict['sequence_number'] is None:
                    values_dict['sequence_number'] = cur_sequence_number
                    cur_sequence_number += 1
                q_exec = connection.execute(question_insert(**values_dict))
                question_id = q_exec.inserted_primary_key[0]
                choices = values_dict.get('choices', [])
                for number, choice in enumerate(choices, start=1):
                    choice_dict = {'question_id': question_id,
                                   'survey_id': survey_id,
                                   'choice': choice,
                                   'choice_number': number}
                    connection.execute(question_choice_insert(**choice_dict))
                    if 'branches' in question_dict:
                        # TODO: branching
                        pass

    return get_one(survey_id)


def delete(survey_id: str):
    """
    Delete the survey specified by the given survey_id

    :param survey_id: the UUID of the survey
    """
    with engine.connect() as connection:
        connection.execute(delete_record(survey_table, 'survey_id', survey_id))
    return {'message': 'Survey deleted'}
