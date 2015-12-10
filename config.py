#!/usr/bin/env python3
"""Default configuration file.

Treat this as a read-only file! It sets the defaults for the configuration
values.

If you want to use different values, set them as command line arguments:

    $ python3 webappy.py --port=8889

or place them in a file called local_config.py (which is in the .gitignore
file). Use the file local_config.py.example for reference.
"""
import os


port = 8888
schema = 'doko'

# The environment variables used here are for the docker-compose up case
# using the regular docker-compose.yml file.
#
# If you are using docker-compose-dev.yml, make sure your local_config.py
# file refers to DB_DEV_PORT_5432_TCP_ADDR, DB_DEV_PORT_5432_TCP_PORT,
# and DB_DEV_ENV_POSTGRES_PASSWORD.
db_host = os.environ.get('DB_PORT_5432_TCP_ADDR', 'localhost')
db_port = os.environ.get('DB_PORT_5432_TCP_PORT', '5432')
db_password = os.environ.get('DB_ENV_POSTGRES_PASSWORD', 'database password')

db_database = 'doko'
db_user = 'postgres'
organization = 'unconfigured organization'

try:
    from local_config import *  # NOQA
except ImportError:
    pass

if __name__ == '__main__':
    options = {k: v for k, v in locals().items() if not k.startswith('__')}
    del options['os']

    import argparse

    description = '''Output the configurations specified in config.py and
    local_config.py'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        'configs',
        metavar='config',
        nargs='*',
        help='configuration option name (default: display all)'
    )
    args = parser.parse_args()

    if args.configs:
        options = {k: options.get(k, None) for k in args.configs}

    for config, value in sorted(options.items()):
        if value is not None:
            print('{} = {!r}'.format(config, value))
        else:
            print(
                '{} = (possibly not a valid configuration'
                ' option.)'.format(config)
            )
