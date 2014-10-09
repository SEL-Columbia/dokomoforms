from sqlalchemy import Table, MetaData

from db import engine


question_table = Table('question', MetaData(bind=engine), autoload=True)


def get_question(question_id):
    select_stmt = question_table.select()
    where_stmt = select_stmt.where(question_table.c.question_id == question_id)
    return where_stmt.execute().first()
