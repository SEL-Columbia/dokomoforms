"""Allow access to the survey table."""
import json

from sqlalchemy import Table, MetaData

from db import engine
from db.question import get_questions


survey_table = Table('question', MetaData(bind=engine), autoload=True)


def survey_json(survey_id) -> str:
    questions = get_questions(survey_id)
    return json.dumps(questions) # lol no
