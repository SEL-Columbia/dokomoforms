#!/usr/bin/env python3
"""Default configuration file.

Treat this as a read-only file! It sets the defaults for the configuration
values.

If you want to use different values, set them as command line arguments:

    $ python3 webappy.py --port=8889

or place them in a file called local_config.py (which is in the .gitignore
file).
"""

port = 8888
schema = 'doko'
db_host = 'localhost:5432'
db_database = 'doko'
db_user = 'postgres'
db_password = 'whatever your password is'
organization = 'unconfigured organization'

# To override this value you must specify it in local_config.py
# You cannot specify it as a command line argument to webapp.py
revisit_url = 'http://localhost:3000/api/v0/facilities.json'

https = True

try:
    from local_config import *  # NOQA
except ImportError:
    pass

if __name__ == '__main__':
    options = {k: v for k, v in locals().items() if not k.startswith('__')}

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
