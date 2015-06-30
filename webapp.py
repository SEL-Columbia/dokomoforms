#!/usr/bin/env python3

"""Main Dokomo Forms entry point.

Execute this script to start the Tornado server and WSGI container. It will
ensure that the proper tables and extensions exist in the specified schema
of the PostgreSQL database.

The application looks for gettext translation files like
locale/{locale}/LC_MESSAGES/dokomoforms.mo
"""
import os.path
import textwrap
import sys
import logging

from sqlalchemy import DDL

from sqlalchemy.orm import sessionmaker

from tornado.web import url
import tornado.httpserver
import tornado.web

from dokomoforms.options import options

if __name__ == '__main__':  # pragma: no cover
    from dokomoforms.options import parse_options
    # Necessary to load the schema properly. Feels like a hack...
    parse_options()

import dokomoforms.handlers as handlers
from dokomoforms.models import create_engine, Base
from dokomoforms.api import (
    SurveyResource, SubmissionResource, NodeResource
)

# =======
# from dokomoforms.models.survey import _set_tzinfos
# >>>>>>> origin/phoenix

_pwd = os.path.dirname(__file__)
bold = '\033[1m'
green = '\033[92m'

UUID_REGEX = '[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][' \
             'a-f0-9]{3}-?[a-f0-9]{12}'


def modify_text(text: str, modifier: str) -> str:
    """Modify text for printing to the command line.

    :param text: the string to modify
    :param modifier: the escape sequence that marks the modifier
    :return: the modified string
    """
    return modifier + text + '\033[0m'


def get_cookie_secret() -> bytes:
    """Return the secret from the cookie_secret file.

    The cookie secret is in the file <project_directory>/cookie_secret. If
    the file doesn't exist, the script will exit with code 1 and tell the
    user how to generate it.

    :return: the cookie secret as bytes
    """
    try:
        with open(os.path.join(_pwd, 'cookie_secret'), 'rb') as cookie_file:
            cookie_secret = cookie_file.read()
        return cookie_secret
    except IOError:
        print(textwrap.fill(
            '{error} no secret key found for creating secure user session'
            ' cookies. Create it by running the following command:'.format(
                error=modify_text('Error:', bold)
            )
        ))
        print('head -c 24 /dev/urandom > cookie_secret')
        sys.exit(1)


def ensure_that_user_wants_to_drop_schema():
    """Check that user asked to drop the schema intentionally.

    Interrogates the user to make sure that the schema specified by
    options.schema should be dropped. If the user decides against it,
    exits the application.
    """
    answer = input(textwrap.fill(
        'Do you really want to drop the schema {schema}? Doing so will {erase}'
        ' all the data {permanently} y/n (default n)'.format(
            schema=options.schema,
            erase=modify_text('ERASE', bold),
            permanently=modify_text('PERMANENTLY!!!', bold),
        )
    ) + ' ')
    if answer.lower().startswith('y'):
        schema_check = input('Enter the exact name of the schema to drop: ')
        if schema_check == options.schema:
            return
        else:
            print('"{}" does not match the schema "{}"'.format(
                schema_check, options.schema
            ))
    print('Not dropping the schema. Exiting...')
    sys.exit()


class Application(tornado.web.Application):

    """The tornado.web.Application for Dokomo Forms."""

    def __init__(self):
        """Set up the application with handlers and a db connection.

        Defines the URLs (with associated handlers) and settings for the
        application, drops the database schema (if the user selected that
        option), then prepares the database and creates a session.

        """
        self._api_version = 'v0'
        self._api_root_path = '/api/' + self._api_version

        urls = [
            # Administrative
            url(r'/', handlers.Index, name='index'),
            url(r'/user/login/?', handlers.Login, name='login'),
            url(r'/user/logout/?', handlers.Logout, name='logout'),

            # Pages
            url(r'/enumerate/({})/?'.format(UUID_REGEX),
                handlers.Enumerate, name="enumerate"),

            # API
            ## Surveys
            url(r'' + self._api_root_path + '/surveys/?',
                SurveyResource.as_list(), name="surveys"),
            url(r'' + self._api_root_path +
                '/surveys/({})/?'.format(UUID_REGEX),
                SurveyResource.as_detail(),
                name="survey"),
            url(r'' + self._api_root_path +
                '/surveys/({})/submit/?'.format(UUID_REGEX),
                SurveyResource.as_view('submit'),
                name="submit_to_survey"),
            url(r'' + self._api_root_path +
                '/surveys/({})/submissions/?'.format(UUID_REGEX),
                SurveyResource.as_view('list_submissions'),
                name="survey_list_submissions"),
            url(r'' + self._api_root_path +
                '/surveys/({})/stats/?'.format(UUID_REGEX),
                SurveyResource.as_view('stats'),
                name="survey_stats"),
            url(r'' + self._api_root_path +
                '/surveys/({})/activity/?'.format(UUID_REGEX),
                SurveyResource.as_view('activity'),
                name="survey_activity"),
            url(r'' + self._api_root_path +
                '/surveys/activity/?'.format(UUID_REGEX),
                SurveyResource.as_view('activity_all'),
                name="activity_all"),

            ## Submissions
            url(r'' + self._api_root_path + '/submissions',
                SubmissionResource.as_list(), name="submissions"),
            url(r'' + self._api_root_path +
                '/submissions/({})/?'.format(UUID_REGEX),
                SubmissionResource.as_detail(),
                name="submission"),

            # Nodes
            url(r'' + self._api_root_path + '/nodes',
                NodeResource.as_list(), name="nodes"),
            url(r'' + self._api_root_path +
                '/nodes/({})/?'.format(UUID_REGEX),
                NodeResource.as_detail(),
                name="node"),
        ]

        # Debug
        if options.debug:
            urls += [
                url(r'/debug/create/(.+)/?',
                    handlers.DebugUserCreationHandler),
                url(r'/debug/login/(.+)/?', handlers.DebugLoginHandler),
                url(r'/debug/logout/?', handlers.DebugLogoutHandler),
            ]

        settings = {
            'template_path': os.path.join(_pwd, 'dokomoforms/templates'),
            'static_path': os.path.join(_pwd, 'dokomoforms/static'),
            'default_handler_class': handlers.NotFound,
            'xsrf_cookies': False,
            'cookie_secret': get_cookie_secret(),
            'login_url': '/',
            'debug': options.dev or options.debug,
            'autoreload': options.dev or options.autoreload
        }
        super().__init__(urls, **settings)
        self.engine = create_engine()
        if options.kill:
            logging.info('Dropping schema {}.'.format(options.schema))
            self.engine.execute(
                DDL('DROP SCHEMA IF EXISTS {} CASCADE'.format(options.schema))
            )
        Base.metadata.create_all(self.engine)
        self.sessionmaker = sessionmaker(bind=self.engine, autocommit=True)
        self.session = self.sessionmaker()
# =======
#         _set_tzinfos()
#         self.session = sessionmaker(bind=self.engine, autocommit=True)()
# >>>>>>> origin/phoenix


def main():  # pragma: no cover
    """Start the Tornado web server."""
    if options.kill:
        ensure_that_user_wants_to_drop_schema()
    http_server = tornado.httpserver.HTTPServer(Application())
    tornado.locale.load_gettext_translations(
        os.path.join(_pwd, 'locale'), 'dokomoforms'
    )
    logging.info(
        '{dokomo}{starting}'.format(
            dokomo=modify_text(
                'Dokomo Forms for {}: '.format(options.organization), bold
            ),
            starting=modify_text(
                'starting server on port {}'.format(options.port), green
            ),
        )
    )
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':  # pragma: no cover
    main()
