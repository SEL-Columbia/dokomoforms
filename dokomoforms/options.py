"""All the application options are defined here.

If you need to inject options at runtime (for testing, etc...):

    from dokomoforms.options import parse_options

    parse_options(name1=value1, name2=value2, ...)
"""
import os.path

import tornado.options
from tornado.options import define, options

__all__ = ('options',)
_arg = None

define(
    'minigrid_website_url', default='http://localhost:8888',
    help='The URL of this instance of the minigrid server.'
)
define('redis_url', default='redis://localhost:6379/0')

# Application options
define('demo', default=False, help='whether to run in demo mode', type=bool)
define('port', help='run on the given port', type=int)

log_help = 'whether to write logs to files in logs/'
define('log_to_file', default=True, help=log_help, type=bool)

define('debug', default=False, help='whether to enable debug mode', type=bool)

https_help = 'whether the application accepts https traffic'
define('https', default=True, help=https_help, type=bool)

define('organization', help='the name of your organization')
define('admin_email', help='the e-mail address of the main administrator')
define('admin_name', help='the user name of the main administrator')

revisit_url = 'https://revisit.global/api/v0/facilities.json'
revisit_help = (
    'the URL for facility data. Do not change this without a good reason.'
)
define('revisit_url', default=revisit_url, help=revisit_help)

# Database options
define('schema', help='database schema name')
define('db_host', help='database host')
define('db_port', help='database port')
define('db_database', help='database name')
define('db_user', help='database user')
define('db_password', help='database password')

pool_help = (
    'the number of database connections to keep in the pool. You can usually'
    ' leave this unchanged.'
)
define('pool_size', default=None, help=pool_help, type=int)

max_overflow_help = (
    'the maximum number of database connections open at once. You can usually'
    ' leave this unchanged.'
)
define('max_overflow', default=None, help=max_overflow_help, type=int)

kill_help = 'whether to drop the existing schema before starting'
define('kill', default=False, help=kill_help, type=bool)


def inject_options(**kwargs):
    """Add extra options programmatically.

    dokomoforms.options.parse_options reads from sys.argv if
    dokomoforms.options._arg is None. Calling
    dokomoforms.options.inject_options(name1='value1', name2='value2', ...) at
    the top of a file injects the given options instead.

    :param kwargs: name='value' arguments like the ones that would be passed
                   to webapp.py as --name=value or set in local_config.py as
                   name = 'value'
    """
    global _arg
    # The first element doesn't get read by tornado.options.parse_command_line,
    # so we might as well set it to None
    new_arg = [None]
    new_arg.extend(
        '--{name}={value}'.format(name=k, value=kwargs[k]) for k in kwargs
    )
    _arg = new_arg


def parse_options():
    """tornado.options.parse_command_line doesn't cut it.

    Tells Tornado to read from the config.py file (which in turn reads from
    the local_config.py file), then from options specified by
    dokomoforms.options._arg (sys.argv if _arg is None, or the list of
    options in _arg otherwise).

    See dokomoforms.options.inject_options
    """
    tornado.options.parse_config_file(
        os.path.join(os.path.dirname(__file__), '..', 'config.py')
    )
    tornado.options.parse_command_line(_arg)
