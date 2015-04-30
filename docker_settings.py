import os

env = os.environ
pg2_string = 'postgresql+psycopg2://postgres:password@{}:{}/doko'
CONNECTION_STRING = pg2_string.format(
    env['DB_PORT_5432_TCP_ADDR'], env['DB_PORT_5432_TCP_PORT']
)
