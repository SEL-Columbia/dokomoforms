"""View functions for submitting a survey."""
from db import engine
from db.question import question_insert
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
