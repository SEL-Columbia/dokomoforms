"""
Module for creating/tearing down the database, both
for the real production server and unit tests.

"""
from argparse import ArgumentParser
import os.path

from sqlalchemy import create_engine
from dokomoforms.db import metadata

from dokomoforms.settings import CONNECTION_STRING, \
        DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

from psycopg2 import connect
import os


killall = 'killall.sql'
extensions = ['uuid.sql', 'postgis.sql']
fixtures = ['type_constraint_fixture.sql']

schema_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)
), 'schema')


def create_db(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
              host=DB_HOST, port=DB_PORT):
    with connect(database='postgres',
                 user='postgres',
                 password=password,
                 host=host,
                 port=port) as conn:
        # auto commit in order to create db
        conn.set_isolation_level(0)
        cur = conn.cursor()
        cur.execute('CREATE DATABASE %s' % dbname)
        conn.set_isolation_level(1)


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


def check_and_create_db(dbname=DB_NAME, user=DB_USER,
                        password=DB_PASSWORD, host=DB_HOST, port=DB_PORT):
    """Check if db and the structures exists, if it does, then
       do nothing, else
       create db and create structures."""
    db_created = False
    try:
        conn = connect(database=dbname, user=user, password=password,
                       host=host, port=port)
        conn.close()
        return
    except Exception:
        print('Creating database and populate tables')
        create_db()
        eng = create_engine(CONNECTION_STRING, convert_unicode=True)
        init_db(eng)
        return


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
