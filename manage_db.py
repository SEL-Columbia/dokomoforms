"""
Module for creating/tearing down the database, both
for the real production server and unit tests.

"""
from argparse import ArgumentParser
import os.path

from sqlalchemy import create_engine
from dokomoforms.db import metadata

from dokomoforms.settings import CONNECTION_STRING

from psycopg2 import connect
import os


killall = 'killall.sql'
extensions = ['uuid.sql', 'postgis.sql']
fixtures = ['type_constraint_fixture.sql']

schema_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)
), 'schema')


def create_db():
    with connect(database='postgres',
                 user='postgres',
                 password='password',
                 host=os.environ['DB_PORT_5432_TCP_ADDR'],
                 port=os.environ['DB_PORT_5432_TCP_PORT']) as conn:
        # auto commit in order to create db
        conn.set_isolation_level(0)
        cur = conn.cursor()
        cur.execute('CREATE DATABASE doko')


def init_db(engine):
    """Create all the tables and insert the fixtures."""
    with engine.begin() as connection:
        for file_path in extensions:
            with open(os.path.join(schema_dir, file_path)) as sqlfile:
                connection.execute(sqlfile.read())
    metadata.create_all(engine)
    with engine.begin() as connection:
        for file_path in fixtures:
            with open(os.path.join(schema_dir, file_path)) as sqlfile:
                connection.execute(sqlfile.read())


def kill_db(engine):
    """Drop the database."""
    with engine.begin() as connection:
        with open(os.path.join(schema_dir, killall)) as sqlfile:
            connection.execute(sqlfile.read())


if __name__ == '__main__':
    parser = ArgumentParser(description='Create or kill the database.')

    group = parser.add_mutually_exclusive_group()  # create xor drop
    chelp = 'The default choice. Create the db using the connection string.'
    group.add_argument('-c', '--create', action='store_true', help=chelp)
    dhelp = 'Drop the db using the connection string.'
    group.add_argument('-d', '--drop', action='store_true', help=dhelp)

    connhelp = 'Optional, defaults to the one specified in settings.py'
    parser.add_argument('CONNECTION_STRING', nargs='?', help=connhelp)

    args = parser.parse_args()

    # create database doko
    create_db()

    # Create the engine using the user-given connection string, if provided
    args_conn = args.CONNECTION_STRING
    conn = args_conn if args_conn is not None else CONNECTION_STRING
    eng = create_engine(conn, convert_unicode=True)

    # Create or kill the db, according to the user's choice
    kill_db(eng) if args.drop else init_db(eng)
