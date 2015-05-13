#!/usr/bin/env python3

"""
Execute this file to start the Tornado server and wsgi container.
"""

import logging
import os.path
import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.web import url
from tornado.options import define, options
import dokomoforms.handlers as handlers
from dokomoforms.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

define('port', help='run on the given port', type=int)
define('cookie_secret', help='string used to create session cookies')
define('debug', default=False, help='whether to enable debug mode', type=bool)

# TODO: move these?
define('db_host', help='database host')
define('db_database', help='database name')
define('db_user', help='database user')
define('db_password', help='database password')

_pwd = os.path.dirname(__file__)
header_color = '\033[1m'
msg_color = '\033[92m'
end_color = '\033[0m'


class Application(tornado.web.Application):
    def __init__(self):
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
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)


def main():
    tornado.options.parse_config_file(os.path.join(_pwd, 'config.py'))
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(
        Application(),
        # ssl_options={
        #     'certfile': '/path/to/cert',
        #     'keyfile': '/path/to/key',
        # },
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
