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
from dokomoforms.options import options, parse_options
import dokomoforms.handlers as handlers
from dokomoforms.models import Base, create_engine
from sqlalchemy import DDL
from sqlalchemy.orm import sessionmaker


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
        self.engine = create_engine()
        if options.kill:
            self.engine.execute(
                DDL('DROP SCHEMA IF EXISTS {} CASCADE'.format(options.schema))
            )
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)


def main():
    parse_options()
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
    http_server = tornado.httpserver.HTTPServer(Application())
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
