#!/usr/bin/env python3

"""
Execute this script to start the Tornado server and wsgi container. It will
ensure that the proper tables and extensions exist in the specified schema.
"""

import logging
import os.path
import sys
import textwrap
import tornado.ioloop
import tornado.locale
import tornado.web
import tornado.httpserver
from tornado.web import url
from dokomoforms.options import options
import dokomoforms.handlers as handlers
from dokomoforms.models import Base, create_engine
from sqlalchemy import DDL
from sqlalchemy.orm import sessionmaker


_pwd = os.path.dirname(__file__)
begin_bold = '\033[1m'
begin_green = '\033[92m'
end_modify = '\033[0m'


def bold(text):
    return begin_bold + text + end_modify


def colorize(text):
    return begin_green + text + end_modify


def get_cookie_secret():
    try:
        return open(os.path.join(_pwd, 'cookie_secret'), 'rb').read()
    except IOError:
        print(textwrap.fill(
            '{error} no secret key found for creating secure user session'
            ' cookies. Create it by running the following command:'.format(
                error=bold('Error:')
            )
        ))
        print('head -c 24 /dev/urandom > cookie_secret')
        sys.exit(1)


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
            'cookie_secret': get_cookie_secret(),
            'login_url': '/',
            'debug': options.debug,
        }
        super().__init__(urls, **settings)
        self.engine = create_engine()
        if options.kill:
            logging.info('Dropping schema {}.'.format(options.schema))
            self.engine.execute(
                DDL('DROP SCHEMA IF EXISTS {} CASCADE'.format(options.schema))
            )
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)


def ensure_that_user_wants_to_drop_schema():
    answer = input(textwrap.fill(
        'Do you really want to drop the schema {schema}? Doing so will {erase}'
        ' all the data {permanently} y/n (default n)'.format(
            schema=options.schema,
            erase=bold('ERASE'),
            permanently=bold('PERMANENTLY!!!'),
        )
    ) + ' ')
    if answer.lower().startswith('y'):
        schema_check = input('Enter the exact name of the schema to drop: ')
        if schema_check == options.schema:
            return
    print('Not dropping the schema. Exiting...')
    sys.exit()


def main():
    if options.kill:
        ensure_that_user_wants_to_drop_schema()
    http_server = tornado.httpserver.HTTPServer(Application())
    tornado.locale.load_gettext_translations(
        os.path.join(_pwd, 'locale'), 'dokomoforms'
    )
    logging.info(
        '{dokomo}{starting}'.format(
            dokomo=bold('Dokomo Forms: '),
            starting=colorize(
                'starting server on port {}'.format(options.port)
            ),
        )
    )
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
