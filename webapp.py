#!/usr/bin/env python3

"""
Execute this script to start the Tornado server and wsgi container. It will
ensure that the proper tables and extensions exist in the specified schema.
"""

import logging
import os.path
import tornado.ioloop
import tornado.locale
import tornado.web
import tornado.httpserver
from tornado.web import url
from tornado.options import define, options
from sqlalchemy import create_engine, event, DDL
from sqlalchemy.orm import sessionmaker

# Application options
define('port', help='run on the given port', type=int)
define('cookie_secret', help='string used to create session cookies')
define('debug', default=False, help='whether to enable debug mode', type=bool)

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

_pwd = os.path.dirname(__file__)
header_color = '\033[1m'
msg_color = '\033[92m'
end_color = '\033[0m'


class Application(tornado.web.Application):
    def __init__(self, *, handlers, Base, kill):
        urls = [
            # Administrative
            url(r'/', handlers.Index, name='index'),
            url(r'/user/login/?', handlers.Login, name='login'),
            url(r'/user/logout/?', handlers.Logout, name='logout'),
        ]
        settings = {
            'template_path': os.path.join(_pwd, 'dokomoforms/templates'),
            'static_path': os.path.join(_pwd, 'dokomoforms/static'),
            'default_handler_class': handlers.NotFound,
            'xsrf_cookies': True,
            'cookie_secret': options.cookie_secret,
            'login_url': '/',
            'debug': options.debug,
        }
        super().__init__(urls, **settings)
        # TODO: configurable?
        self.engine = create_engine(
            'postgresql+psycopg2://{}:{}@{}/{}'.format(
                options.db_user,
                options.db_password,
                options.db_host,
                options.db_database,
            ),
            convert_unicode=True,
            pool_size=0,
            max_overflow=-1,
        )
        if kill:
            self.engine.execute(
                DDL('DROP SCHEMA IF EXISTS {} CASCADE'.format(options.schema))
            )
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        event.listen(
            Base.metadata,
            'before_create',
            DDL(
                'CREATE SCHEMA IF NOT EXISTS {schema};'
                'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'
                ' WITH SCHEMA pg_catalog;'.format(schema=options.schema)
            )
        )
        Base.metadata.create_all(self.engine)


def main():
    tornado.options.parse_config_file(os.path.join(_pwd, 'config.py'))
    tornado.options.parse_command_line()
    import dokomoforms.handlers as handlers
    from dokomoforms.models import Base
    if options.cookie_secret is None:  # TODO: move into a function
        print('You must set cookie_secret in local_config.py!')
        return
    if options.kill:  # TODO: move this into a "warning" function
        answer = input(
            'Do you really want to drop the schema {}? y/n '
            '(Default n) '.format(options.schema)
        )
        if not answer.lower().startswith('y'):
            print('Not dropping the schema. Exiting.')
            return
    http_server = tornado.httpserver.HTTPServer(
        Application(
            handlers=handlers,
            Base=Base,
            kill=options.kill,
        )
    )
    tornado.locale.load_gettext_translations(
        os.path.join(_pwd, 'locale'), 'dokomoforms'
    )
    logging.info(
        '{}Dokomo Forms: {}{}starting server on port {}{}'.format(
            header_color, end_color, msg_color, options.port, end_color
        )
    )
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
