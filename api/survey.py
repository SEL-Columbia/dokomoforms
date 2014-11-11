"""Functions for interacting with surveys."""
from collections import Iterator

from sqlalchemy.engine import RowProxy, Connection

from api import execute_with_exceptions
from db import engine, update_record, delete_record
from db.question import question_insert, get_questions, question_table, \
    get_free_sequence_number, question_select
from db.question_branch import get_branches, question_branch_insert, \
    question_branch_table, MultipleBranchError
from db.question_choice import get_choices, question_choice_insert, \
    question_choice_table, RepeatedChoiceError
from db.survey import survey_insert, survey_select, survey_table, \
    SurveyAlreadyExistsError, get_free_title
from db.type_constraint import TypeConstraintDoesNotExistError


def _create_choices(connection: Connection,
                    values: dict,
                    question_id: str) -> Iterator:
    """
    Create choices as part of a survey submission.

    :param connection: the SQLAlchemy Connection object for the transaction
    :param values: the dictionary of values associated with the question
    :param question_id: the UUID of the question
    """
    for number, choice in enumerate(values.get('choices', [])):
        choice_dict = {'question_id': question_id,
                       'survey_id': values['survey_id'],
                       'choice': choice,
                       'choice_number': number,
                       'type_constraint_name': values['type_constraint_name'],
                       'question_sequence_number': values['sequence_number'],
                       'allow_multiple': values['allow_multiple']}
        executable = question_choice_insert(**choice_dict)
        exc = [('unique_choice_names', RepeatedChoiceError(choice))]
        result = execute_with_exceptions(connection, executable, exc)

        yield result.inserted_primary_key[0]


def _create_questions(connection: Connection,
                      questions: list,
                      survey_id: str) -> Iterator:
    """
    Create questions as part of a survey submission.

    :param connection: the SQLAlchemy Connection object for the transaction
    :param questions: the dictionary of values associated with the question
    :param survey_id: the UUID of the survey
    """
    for number, question in enumerate(questions):
        values = question.copy()
        values['sequence_number'] = number
        values['survey_id'] = survey_id
        executable = question_insert(**values)
        tcn = values['type_constraint_name']
        exceptions = [('question_type_constraint_name_fkey',
                       TypeConstraintDoesNotExistError(tcn))]
        result = execute_with_exceptions(connection, executable, exceptions)
        question_primary_key = result.inserted_primary_key
        q_id = question_primary_key[0]
        if values['allow_multiple'] is None:
            values['allow_multiple'] = False
        choices = list(_create_choices(connection, values, q_id))

        yield {'question_id': q_id,
               'type_constraint_name': tcn,
               'sequence_number': question_primary_key[2],
               'allow_multiple': values['allow_multiple'],
               'choice_ids': choices}


def _create_branches(connection: Connection,
                     questions_json: list,
                     question_dicts: list,
                     survey_id: str):
    """
    Create branches as part of a survey submission.

    :param connection: the SQLAlchemy Connection object for the transaction
    :param questions_json: a list of dictionaries coming from the JSON input
    :param question_dicts: a list of dictionaries resulting from inserting
                           the questions
    :param survey_id: the UUID of the survey
    """
    for index, question_dict in enumerate(questions_json):
        for branch in question_dict.get('branches', []):
            choice_index = branch['choice_number']
            from_dict = question_dicts[index]
            question_choice_id = from_dict['choice_ids'][choice_index]
            from_question_id = from_dict['question_id']
            from_tcn = question_dict['type_constraint_name']
            from_mul = from_dict['allow_multiple']
            to_question_index = branch['to_question_number']
            to_question_id = question_dicts[to_question_index]['question_id']
            to_tcn = question_dicts[to_question_index]['type_constraint_name']
            to_seq = question_dicts[to_question_index]['sequence_number']
            to_mul = question_dicts[to_question_index]['allow_multiple']
            branch_dict = {'question_choice_id': question_choice_id,
                           'from_question_id': from_question_id,
                           'from_type_constraint': from_tcn,
                           'from_sequence_number': index,
                           'from_allow_multiple': from_mul,
                           'from_survey_id': survey_id,
                           'to_question_id': to_question_id,
                           'to_type_constraint': to_tcn,
                           'to_sequence_number': to_seq,
                           'to_allow_multiple': to_mul,
                           'to_survey_id': survey_id}
            executable = question_branch_insert(**branch_dict)
            exc = [('question_branch_from_question_id_question_choice_id_key',
                    MultipleBranchError(question_choice_id))]
            execute_with_exceptions(connection, executable, exc)


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

    with engine.begin() as connection:
        # First, create an entry in the survey table
        survey_values = {  # 'auth_user_id': user_id,
                           'title': get_free_title(title)}
        executable = survey_insert(**survey_values)
        exc = [
            ('survey_title_survey_owner_key', SurveyAlreadyExistsError(title))]
        result = execute_with_exceptions(connection, executable, exc)
        survey_id = result.inserted_primary_key[0]

        # Now insert questions.  Inserting branches has to come afterward so
        # that the question_id values actually exist in the tables.
        questions = list(_create_questions(connection, data_q, survey_id))
        _create_branches(connection, data_q, questions, survey_id)

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
# def get_all(data: dict) -> dict:
def get_all() -> dict:
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
    cur_sequence_number = get_free_sequence_number(survey_id)

    with engine.connect() as connection:
        if 'title' in data:
            values = {'title': data['title']}
            s_upd = update_record(survey_table, 'survey_id', survey_id, values)
            connection.execute(s_upd)

        question_ids = []
        for question_dict in data.get('questions', []):
            values_dict = question_dict.copy()
            if 'question_id' in values_dict:
                # update existing question
                q_id = values_dict.pop('question_id')
                question_ids.append(q_id)
                choices = values_dict.pop('choices', [])
                values_dict.pop('branches', [])
                # values_dict may now be empty if the only changes are to
                # choices/branches
                if values_dict:
                    q_upd = update_record(question_table, 'question_id', q_id,
                                          values_dict)
                    connection.execute(q_upd)
                if choices:
                    question = question_select(q_id)
                    # delete the existing choices and replace them with the
                    # new ones
                    for choice in get_choices(q_id).fetchall():
                        ch_id = choice.question_choice_id
                        tbl = question_choice_table
                        d_ch = delete_record(tbl, 'question_choice_id', ch_id)
                        connection.execute(d_ch)
                    for number, choice in enumerate(choices):
                        tcn = question.type_constraint_name
                        seq = question.sequence_number
                        mul = question.allow_multiple
                        ch_dict = {'question_id': q_id,
                                   'survey_id': survey_id,
                                   'choice': choice,
                                   'choice_number': number,
                                   'type_constraint_name': tcn,
                                   'question_sequence_number': seq,
                                   'allow_multiple': mul}
                        connection.execute(question_choice_insert(**ch_dict))
            else:
                # create new question
                values_dict['survey_id'] = survey_id
                if values_dict['sequence_number'] is None:
                    values_dict['sequence_number'] = cur_sequence_number
                    cur_sequence_number += 1
                q_exec = connection.execute(question_insert(**values_dict))
                question_id = q_exec.inserted_primary_key[0]
                question_ids.append(question_id)
                choices = values_dict.get('choices', [])
                for number, choice in enumerate(choices):
                    tcn = q_exec.inserted_primary_key[1]
                    seq = q_exec.inserted_primary_key[2]
                    mul = q_exec.inserted_primary_key[3]
                    choice_dict = {'question_id': question_id,
                                   'survey_id': survey_id,
                                   'choice': choice,
                                   'choice_number': number,
                                   'type_constraint_name': tcn,
                                   'question_sequence_number': seq,
                                   'allow_multiple': mul}
                    connection.execute(question_choice_insert(**choice_dict))
        # deal with branches
        for index, question_dict in enumerate(data.get('questions', [])):
            from_question_id = question_ids[index]
            from_question = question_select(from_question_id)
            from_seq = from_question.sequence_number
            if 'branches' in question_dict:
                # delete the existing branches
                for old_branch in get_branches(from_question_id).fetchall():
                    b_id = old_branch.question_branch_id
                    tbl = question_branch_table
                    d_br = delete_record(tbl, 'question_branch_id', b_id)
                    connection.execute(d_br)
            # insert the new branches
            for branch in question_dict.get('branches', []):
                all_choices = get_choices(from_question_id).fetchall()
                choice_number = branch['choice_number']
                choice_id = all_choices[choice_number].question_choice_id
                from_tcn = from_question.type_constraint_name
                from_mul = from_question.allow_multiple
                to_question_index = branch['to_question_number']
                all_questions = get_questions(survey_id).fetchall()
                to_question = all_questions[to_question_index]
                to_question_id = to_question.question_id
                to_tcn = to_question.type_constraint_name
                to_seq = to_question.sequence_number
                to_mul = to_question.allow_multiple
                branch_dict = {'question_choice_id': choice_id,
                               'from_question_id': from_question_id,
                               'from_type_constraint': from_tcn,
                               'from_sequence_number': from_seq,
                               'from_allow_multiple': from_mul,
                               'from_survey_id': survey_id,
                               'to_question_id': to_question_id,
                               'to_type_constraint': to_tcn,
                               'to_sequence_number': to_seq,
                               'to_allow_multiple': to_mul,
                               'to_survey_id': survey_id}
                connection.execute(question_branch_insert(**branch_dict))

    return get_one(survey_id)


def delete(survey_id: str):
    """
    Delete the survey specified by the given survey_id

    :param survey_id: the UUID of the survey
    """
    with engine.connect() as connection:
        connection.execute(delete_record(survey_table, 'survey_id', survey_id))
    return {'message': 'Survey deleted'}
