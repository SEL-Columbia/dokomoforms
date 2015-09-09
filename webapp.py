#!/usr/bin/env python3
"""Main Dokomo Forms entry point.

Execute this script to start the Tornado server and WSGI container. It will
ensure that the proper tables and extensions exist in the specified schema
of the PostgreSQL database.

The application looks for gettext translation files like
locale/{locale}/LC_MESSAGES/dokomoforms.mo
"""
import os
import textwrap
import signal
import subprocess
import sys
from time import sleep
import logging
import mimetypes

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
from dokomoforms.models import create_engine, Base, UUID_REGEX
from dokomoforms.handlers.api import (
    SurveyResource, SubmissionResource, PhotoResource, NodeResource
)


_pwd = os.path.dirname(__file__)
bold = '\033[1m'
green = '\033[92m'

# Add mimetypes
mimetypes.add_type("application/x-font-woff", ".woff")
mimetypes.add_type("application/octet-stream", ".ttf")


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


API_VERSION = 'v0'
API_ROOT_PATH = '/api/' + API_VERSION


def api_url(path, *args, **kwargs):
    """Prepend the API path to API URLs."""
    return url(
        (r'' + API_ROOT_PATH + path).format(uuid=UUID_REGEX),
        *args, **kwargs
    )


class Application(tornado.web.Application):

    """The tornado.web.Application for Dokomo Forms."""

    def __init__(self, session=None):
        """Set up the application with handlers and a db connection.

        Defines the URLs (with associated handlers) and settings for the
        application, drops the database schema (if the user selected that
        option), then prepares the database and creates a session.
        """
        self._api_version = API_VERSION
        self._api_root_path = API_ROOT_PATH

        sur = SurveyResource

        urls = [
            # Administrative
            url(r'/', handlers.Index, name='index'),
            url(r'/user/login/?', handlers.Login, name='login'),
            url(r'/user/logout/?', handlers.Logout, name='logout'),

            # Views
            # * Admin views
            url(
                r'/view/({})/?'.format(UUID_REGEX),
                handlers.ViewSurveyHandler,
                name='admin_survey_view',
            ),
            url(
                r'/view/data/({})/?'.format(UUID_REGEX),
                handlers.ViewSurveyDataHandler,
                name='admin_data_view',
            ),
            url(
                r'/view/submission/({})/?'.format(UUID_REGEX),
                handlers.ViewSubmissionHandler,
                name='admin_submission_view',
            ),

            url(
                r'/view/user-administration/?',
                handlers.ViewUserAdminHandler,
                name='admin_user_view',
            ),

            # * Regular views
            url(
                r'/enumerate/({})/?'.format(UUID_REGEX), handlers.Enumerate,
                name='enumerate'
            ),
            url(
                r'/enumerate/(.+)/?', handlers.EnumerateTitle,
                name='enumerate_title'
            ),

            # API
            # * Surveys
            api_url('/surveys/?', sur.as_list(), name='surveys'),
            api_url('/surveys/({uuid})/?', sur.as_detail(), name='survey'),
            api_url(
                '/surveys/({uuid})/submit/?', sur.as_view('submit'),
                name='submit_to_survey'
            ),
            api_url(
                '/surveys/({uuid})/submissions/?',
                sur.as_view('list_submissions'),
                name='survey_list_submissions',
            ),
            api_url(
                '/surveys/({uuid})/stats/?', sur.as_view('stats'),
                name='survey_stats'
            ),
            api_url(
                '/surveys/({uuid})/activity/?', sur.as_view('activity'),
                name='survey_activity'
            ),
            api_url(
                '/surveys/activity/?', sur.as_view('activity_all'),
                name='activity_all'
            ),

            # * Submissions
            api_url(
                '/submissions/?', SubmissionResource.as_list(),
                name='submissions'
            ),
            api_url(
                '/submissions/({uuid})/?', SubmissionResource.as_detail(),
                name='submission'
            ),
            api_url('/photos/?', PhotoResource.as_list(), name='photos'),
            api_url(
                '/photos/({uuid})/?', PhotoResource.as_detail(), name='photo'
            ),

            # * Nodes
            api_url('/nodes/?', NodeResource.as_list(), name='nodes'),
            api_url(
                '/nodes/({uuid})/?', NodeResource.as_detail(), name='node'
            ),

            # * Users
            api_url(
                '/user/generate-api-token/?', handlers.GenerateToken,
                name='generate_token'
            ),
        ]

        settings = {
            'template_path': os.path.join(_pwd, 'dokomoforms/templates'),
            'static_path': os.path.join(_pwd, 'dokomoforms/static'),
            'default_handler_class': handlers.NotFound,
            'xsrf_cookies': True,
            'cookie_secret': get_cookie_secret(),
            'login_url': '/',
            'debug': options.dev or options.debug,
            'autoreload': options.dev or options.autoreload,
        }

        # Debug
        if settings['debug']:  # pragma: no cover
            urls += [
                url(r'/debug/create/(.+)/?',
                    handlers.DebugUserCreationHandler),
                url(r'/debug/login/(.+)/?', handlers.DebugLoginHandler),
                url(r'/debug/logout/?', handlers.DebugLogoutHandler),
                url(r'/debug/persona_verify/?', handlers.DebugPersonaHandler),
                url(r'/debug/facilities/?', handlers.DebugRevisitHandler),
                url(r'/debug/toggle_facilities/?',
                    handlers.DebugToggleRevisitHandler),
            ]

        super().__init__(urls, **settings)

        # Database setup
        if session is None:
            engine = create_engine()
            if options.kill:
                logging.info('Dropping schema {}.'.format(options.schema))
                engine.execute(DDL(
                    'DROP SCHEMA IF EXISTS {} CASCADE'.format(options.schema)
                ))
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine, autocommit=True)
            self.session = Session()
        else:
            self.session = session


def start_http_server(http_server, port):  # pragma: no cover
    """Start the server, with the option to kill anything using the port."""
    try:
        http_server.listen(options.port)
    except OSError:
        pid = (
            subprocess
            .check_output(['lsof', '-t', '-i:{}'.format(options.port)])
            .decode()
            .strip()
        )
        cmd = (
            subprocess
            .check_output(['ps', '-o', 'cmd', '-fp', pid, '--no-header'])
            .decode()
            .strip()
        )
        msg = (
            'A process (ID: {} CMD: {})'
            ' is currently using port {}'.format(pid, cmd, port)
        )
        print(msg)
        replace = input('Do you want to kill it? y/n (default n) ')
        if replace.lower().startswith('y'):
            os.killpg(int(pid), signal.SIGTERM)
            sleep(1)
            print('Killed process {}'.format(pid))
            http_server.listen(options.port)
        else:
            raise


def main(msg=None):  # pragma: no cover
    """Start the Tornado web server."""
    if options.kill:
        ensure_that_user_wants_to_drop_schema()
    http_server = tornado.httpserver.HTTPServer(Application())
    tornado.locale.load_gettext_translations(
        os.path.join(_pwd, 'locale'), 'dokomoforms'
    )
    start_http_server(http_server, options.port)
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
    if msg is not None:
        print(msg)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':  # pragma: no cover
    main()
