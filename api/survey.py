"""Functions for interacting with surveys."""
from collections import Iterator

from sqlalchemy.engine import RowProxy, Connection

from api import execute_with_exceptions
from db import engine, update_record, delete_record
from db.question import question_insert, get_questions, question_table
from db.question_branch import get_branches, question_branch_insert, \
    question_branch_table
from db.question_choice import get_choices, question_choice_insert, \
    question_choice_table
from db.survey import survey_insert, survey_select, survey_table, \
    SurveyAlreadyExistsError, get_free_title
from db.type_constraint import TypeConstraintDoesNotExistError


def _create_or_update_choices(connection: Connection,
                              values: dict,
                              question_id: str) -> Iterator:
    """
    Create or update the choices of a survey question.

    :param connection: the SQLAlchemy Connection object for the transaction
    :param values: the dictionary of values associated with the question
    :param question_id: the UUID of the question
    """
    current = get_choices(question_id)
    existing_choices = {ch.choice: (ch.choice_number,
                                    ch.question_choice_id) for ch in current}
    new_choices = values.get('choices', [])
    new_choice_set = set(new_choices)
    # delete choices that don't exist anymore
    for choice in existing_choices:
        if choice not in new_choice_set:
            connection.execute(delete_record(question_choice_table,
                                             'question_choice_id',
                                             existing_choices[choice][1]))
    for number, choice in enumerate(new_choices):
        if choice in existing_choices:
            choice_number, choice_id = existing_choices[choice]
            if choice_number != number:
                connection.execute(update_record(question_choice_table,
                                                 'question_choice_id',
                                                 choice_id,
                                                 {'choice_number': number}))
            yield choice_id
        else:
            choice_dict = {'question_id': question_id,
                           'survey_id': values['survey_id'],
                           'choice': choice,
                           'choice_number': number,
                           'type_constraint_name': values[
                               'type_constraint_name'],
                           'question_sequence_number': values[
                               'sequence_number'],
                           'allow_multiple': values['allow_multiple']}
            result = connection.execute(question_choice_insert(**choice_dict))
            yield result.inserted_primary_key[0]


def _create_or_update_questions(connection: Connection,
                                questions: list,
                                survey_id: str) -> Iterator:
    """
    Create or updates the questions of a survey.

    :param connection: the SQLAlchemy Connection object for the transaction
    :param questions: a list of dictionaries, each containing the values
                      associated with a question
    :param survey_id: the UUID of the survey
    """
    # delete questions that don't exist anymore
    surviving_questions = {q.get('question_id', None) for q in questions}
    for existing_question in get_questions(survey_id):
        if existing_question.question_id not in surviving_questions:
            connection.execute(delete_record(question_table,
                                             'question_id',
                                             existing_question.question_id))
    for number, question in enumerate(questions):
        values = question.copy()
        values['sequence_number'] = number
        values['survey_id'] = survey_id
        if values['allow_multiple'] is None:
            values['allow_multiple'] = False

        # Deal with creating or updating
        is_update = 'question_id' in values
        if is_update:
            update_values = values.copy()
            question_id = update_values.pop('question_id')
            # Transform any fields supplied as null
            if update_values['hint'] is None:
                update_values['hint'] = ''
            if update_values['required'] is None:
                update_values['required'] = False
            if update_values['logic'] is None:
                update_values['logic'] = {}
            seq = update_values['sequence_number']
            mul = update_values['allow_multiple']
            tcn = update_values['type_constraint_name']
            executable = update_record(question_table,
                                       'question_id',
                                       question_id,
                                       sequence_number=seq,
                                       hint=update_values['hint'],
                                       required=update_values['required'],
                                       allow_multiple=mul,
                                       logic=update_values['logic'],
                                       title=update_values['title'],
                                       type_constraint_name=tcn,
                                       survey_id=update_values['survey_id'])
        else:
            executable = question_insert(**values)

        # Now actually execute the create or update
        tcn = values['type_constraint_name']
        exceptions = [('question_type_constraint_name_fkey',
                       TypeConstraintDoesNotExistError(tcn))]
        result = execute_with_exceptions(connection, executable, exceptions)
        if is_update:
            q_id = values['question_id']
        else:
            q_id = result.inserted_primary_key[0]
        choices = list(_create_or_update_choices(connection, values, q_id))
        yield {'question_id': q_id,
               'type_constraint_name': tcn,
               'sequence_number': values['sequence_number'],
               'allow_multiple': values['allow_multiple'],
               'choice_ids': choices}


def _create_or_update_branches(connection: Connection,
                               questions_json: list,
                               question_dicts: list,
                               survey_id: str):
    """
    Create or update the branches in a survey.

    :param connection: the SQLAlchemy Connection object for the transaction
    :param questions_json: a list of dictionaries coming from the JSON input
    :param question_dicts: a list of dictionaries resulting from inserting
                           the questions
    :param survey_id: the UUID of the survey
    """
    for index, question_dict in enumerate(questions_json):
        from_dict = question_dicts[index]
        from_q_id = from_dict['question_id']

        # delete existing branches, if any
        # this is safe to do for an update
        condition = question_branch_table.c.from_question_id == from_q_id
        connection.execute(question_branch_table.delete().where(condition))
        for branch in question_dict.get('branches', []):
            choice_index = branch['choice_number']
            question_choice_id = from_dict['choice_ids'][choice_index]
            from_tcn = question_dict['type_constraint_name']
            from_mul = from_dict['allow_multiple']
            to_question_index = branch['to_question_number']
            to_question_id = question_dicts[to_question_index]['question_id']
            to_tcn = question_dicts[to_question_index]['type_constraint_name']
            to_seq = question_dicts[to_question_index]['sequence_number']
            to_mul = question_dicts[to_question_index]['allow_multiple']
            branch_dict = {'question_choice_id': question_choice_id,
                           'from_question_id': from_q_id,
                           'from_type_constraint': from_tcn,
                           'from_sequence_number': index,
                           'from_allow_multiple': from_mul,
                           'from_survey_id': survey_id,
                           'to_question_id': to_question_id,
                           'to_type_constraint': to_tcn,
                           'to_sequence_number': to_seq,
                           'to_allow_multiple': to_mul,
                           'to_survey_id': survey_id}
            connection.execute(question_branch_insert(**branch_dict))


def create(data: dict) -> dict:
    """
    Create a survey with questions.

    :param data: a JSON representation of the survey
    :return: the UUID of the survey in the database
    """
    survey_id = None

    # user_id = json_data['auth_user_id']
    title = data['title']
    data_q = data.get('questions', [])

    with engine.begin() as conn:
        # First, create an entry in the survey table
        safe_title = get_free_title(title)
        survey_values = {  # 'auth_user_id': user_id,
                           'title': safe_title}
        executable = survey_insert(**survey_values)
        exc = [
            ('survey_title_survey_owner_key',
             SurveyAlreadyExistsError(safe_title))]
        result = execute_with_exceptions(conn, executable, exc)
        survey_id = result.inserted_primary_key[0]

        # Now insert questions.  Inserting branches has to come afterward so
        # that the question_id values actually exist in the tables.
        questions = list(_create_or_update_questions(conn, data_q, survey_id))
        _create_or_update_branches(conn, data_q, questions, survey_id)

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


def update(data: dict):
    """
    Update a survey (title, questions). You can also add questions here.

    :param data: JSON containing the UUID of the survey and fields to update.
    """
    survey_id = data['survey_id']
    existing_survey = survey_select(survey_id)
    data_q = data.get('questions', [])
    with engine.connect() as conn:
        if existing_survey.title != data['title']:
            safe_title = get_free_title(data['title'])
            executable = update_record(survey_table,
                                       'survey_id',
                                       survey_id,
                                       title=safe_title)
            exc = [('survey_title_survey_owner_key',
                    SurveyAlreadyExistsError(safe_title))]
            execute_with_exceptions(conn, executable, exc)
        questions = list(_create_or_update_questions(conn, data_q, survey_id))
        _create_or_update_branches(conn, data_q, questions, survey_id)

    return get_one(survey_id)


def delete(survey_id: str):
    """
    Delete the survey specified by the given survey_id

    :param survey_id: the UUID of the survey
    """
    with engine.connect() as connection:
        connection.execute(delete_record(survey_table, 'survey_id', survey_id))
    return {'message': 'Survey deleted'}
