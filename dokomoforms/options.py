import os.path
import tornado.options
from tornado.options import define, options

__all__ = ['options']
arg = None

# Application options
define('port', help='run on the given port', type=int)
define('cookie_secret', help='string used to create session cookies')
define('debug', default=False, help='whether to enable debug mode', type=bool)
define(
    'https', help='whether the application accepts https traffic', type=bool
)
define('organization', help='the name of your organization')

# Database options
define('schema', help='database schema name')
define('db_host', help='database host')
define('db_database', help='database name')
define('db_user', help='database user')
define('db_password', help='database password')
define(
    'kill',
    default=False,
    help='whether to drop the existing schema before starting',
    type=bool,
)


def set_arg(new_arg):
    global arg
    arg = new_arg


def parse_options():
    tornado.options.parse_config_file(
        os.path.join(os.path.dirname(__file__), '..', 'config.py')
    )
    tornado.options.parse_command_line(arg)
