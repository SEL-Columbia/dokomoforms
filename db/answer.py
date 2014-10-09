from sqlalchemy import Table, MetaData

from db import engine
from db.question import get_question


answer_table = Table('answer', MetaData(bind=engine), autoload=True)


def answer_insert(*, answer, question_id, submission_id, survey_id):
    question = get_question(question_id)
    type_constraint_name = question.type_constraint_name
    answer_type = 'answer_' + type_constraint_name
    values = {answer_type: answer,
              'question_id': question_id,
              'submission_id': submission_id,
              'type_constraint_name': type_constraint_name,
              'sequence_number': question.sequence_number,
              'allow_multiple': question.allow_multiple,
              'survey_id': survey_id,
              'submission_id': submission_id}
    return answer_table.insert().values(values)
