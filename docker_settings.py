import os
env = os.environ
CONNECTION_STRING = 'postgresql+psycopg2://postgres' \
                    ':password@%s:%s/doko' % (env['DB_PORT_5432_TCP_ADDR'],
                                             env['DB_PORT_5432_TCP_PORT'])
