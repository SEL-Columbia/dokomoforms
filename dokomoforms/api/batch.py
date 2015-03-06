"""Functions for batch operations."""
from functools import partial

from sqlalchemy.engine import Connection

from dokomoforms.api import json_response
from dokomoforms.api.submission import _create_submission
from dokomoforms.db.question import get_required


def submit(connection: Connection, data: dict) -> dict:
    """
    Batch submit to a survey.

    :param connection: a SQLAlchemy connection
    :param data: representation of the submission (from json.loads)
    :return: the UUIDs of the submissions in the database
    """
    c = connection
    survey_id = data['survey_id']
    required_ids = {q.question_id for q in
                    get_required(connection, survey_id)}

    with c.begin():
        create = partial(_create_submission, c, survey_id, required_ids)
        submission_ids = list(map(create, data['submissions']))

    return json_response(submission_ids)
