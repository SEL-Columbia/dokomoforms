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
from dokomoforms.handlers.index import IndexHandler

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
        handlers = [
            url(r'/', IndexHandler, name='index'),
        ]
        settings = {
            'template_path': os.path.join(_pwd, 'templates'),
            'static_path': os.path.join(_pwd, 'static'),
            'xsrf_cookies': True,
            'cookie_secret': options.cookie_secret,
            'login_url': '/',
            'debug': options.debug,
        }
        super().__init__(handlers, **settings)
        self.db = None  # TODO: SQLAlchemy
        self.maybe_create_tables()

    def maybe_create_tables(self):
        pass


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
