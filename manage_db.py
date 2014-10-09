"""
Module for creating/tearing down the database, both
for the real production server and unit tests.

"""

import sys
from os.path import join
from sqlalchemy import create_engine

from settings import CONNECTION_STRING

killall = 'killall.sql'
extensions = ['uuid.sql']
tables = ['auth_user.tbl.sql',
          'survey.tbl.sql',
          'type_constraint.tbl.sql',
          'logical_constraint.tbl.sql',
          'submission.tbl.sql',
          'question.tbl.sql',
          'question_choice.tbl.sql',
          'question_branch.tbl.sql',
          'answer.tbl.sql',
          'answer_choice.tbl.sql']
fixtures = ['type_constraint_fixture.sql',
            'logical_constraint_fixture.sql']


def init_db(engine):
    """Create all the tables and insert the fixtures."""
    with engine.begin() as connection:
        for file_path in extensions + tables + fixtures:
            with open(join('schema', file_path)) as sqlfile:
                connection.execute(sqlfile.read())


def kill_db(engine):
    """Drop the database."""
    with engine.begin() as connection:
        with open(join('schema', killall)) as sqlfile:
            connection.execute(sqlfile.read())


if __name__ == "__main__":
    """Create a command-line main() entry point"""

    # TODO: use argparse?
    if len(sys.argv) < 2:
        # Define the usage
        print(sys.argv[0], '--create (default) or --drop', '[CONNECTION STRING (optional, defaults to one specified in settings.py)]')
    else:
        # determine the db engine
        try:
            # see if there was a custom connection string specified
            eng = create_engine(sys.argv[2], convert_unicode=True)
        except IndexError:
            # use the default connection string from settings.py
            eng = create_engine(CONNECTION_STRING, convert_unicode=True)

        # do the specified action
        if sys.argv[1].lower() == '--drop':
            kill_db(eng)
        else:
            init_db(eng)
