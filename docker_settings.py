import os
env = os.environ

DB_USER = 'postgres'
DB_PASSWORD = 'password'
DB_HOST = env['DB_PORT_5432_TCP_ADDR']
DB_PORT = env['DB_PORT_5432_TCP_PORT']
DB_NAME = 'doko'

pg2_string = 'postgresql+psycopg2://{}:{}@{}:{}/{}'
CONNECTION_STRING = pg2_string.format(
        DB_USER,
        DB_PASSWORD,
        DB_HOST,
        DB_PORT,
        DB_NAME
)
