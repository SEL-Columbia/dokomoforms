"""Module for creating/tearing down the database."""
from os.path import join

from sqlalchemy import create_engine

from settings import CONNECTION_STRING


engine = create_engine(CONNECTION_STRING, convert_unicode=True)

killall = 'killall.sql'
extensions = ['uuid.sql']
tables = ['auth_user.tbl.sql',
          'survey.tbl.sql',
          'type_constraint.tbl.sql',
          'question_variety.tbl.sql',
          'submission.tbl.sql',
          'question.tbl.sql',
          'question_choice.tbl.sql',
          'question_branch.tbl.sql',
          'answer.tbl.sql',
          'answer_choice.tbl.sql']
fixtures = ['type_constraint_fixture.sql',
            'question_variety_fixture.sql']


def init_db():
    """Create all the tables and insert the fixtures."""
    with engine.begin() as connection:
        for file_path in extensions + tables + fixtures:
            with open(join('schema', file_path)) as sqlfile:
                connection.execute(sqlfile.read())


def kill_db():
    """Drop the database."""
    with engine.begin() as connection:
        with open(join('schema', killall)) as sqlfile:
            connection.execute(sqlfile.read())
