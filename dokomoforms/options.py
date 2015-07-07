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

# Application options
define('port', help='run on the given port', type=int)
define('cookie_secret', help='string used to create session cookies')
define('debug', default=False, help='whether to enable debug mode', type=bool)
define('autoreload', default=False, help='whether to autoreload', type=bool)
define('dev',
       default=False,
       help='turn on autoreload and debug, maybe some other dev options',
       type=bool,
       )

define('https',
       help='whether the application accepts https traffic',
       type=bool,
       )
define('organization', help='the name of your organization')

# Database options
define('schema', help='database schema name')
define('db_host', help='database host')
define('db_database', help='database name')
define('db_user', help='database user')
define('db_password', help='database password')
define('TEST_USER', help='A test user for... testing.')
define('kill',
       default=False,
       help='whether to drop the existing schema before starting',
       type=bool,
       )


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
