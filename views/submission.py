"""View functions for submitting answers to a survey."""
from db import engine
from db.answer import answer_insert
from db.submission import submission_insert


def submit(data: str) -> str:
    """
    Create a submission with answers.

    :param data: representation of the submission (from json.loads)
    :return: the UUID of the submission in the database
    """
    submission_id = None

    survey_id = data['survey_id']
    all_answers = data['answers']
    # Filter out the skipped questions in the submission.
    answers = (ans for ans in all_answers if ans['answer'] is not None)

    with engine.begin() as connection:
        submission_values = {'submitter': '',
                             'survey_id': survey_id}
        result = connection.execute(submission_insert(**submission_values))
        submission_id = result.inserted_primary_key[0]

        for answer_dict in answers:
            # Add a few fields to the answer_dict
            value_dict = answer_dict.copy()
            value_dict['submission_id'] = submission_id
            value_dict['survey_id'] = survey_id
            connection.execute(answer_insert(**value_dict))

    return submission_id
