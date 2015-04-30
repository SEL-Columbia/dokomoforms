#!/usr/bin/python

"""
This file defines configuration settings for
running the server software.

"""

from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


#
# General

# DEBUG WARNING
APP_DEBUG = False  # if True, anyone can sign in as any user
# YOU HAVE BEEN WARNED
# Also if you set TEST_USER, that account will be logged-in permanently

LEVELS = {DEBUG, INFO, WARNING, ERROR, CRITICAL}
LOG_LEVEL = ERROR  # for testing, use DEBUG in a local_settings.py file instead

#
# Database

DB_USER = 'postgres'
DB_PASSWORD = 'password'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'doko'

pg2_string = 'postgresql+psycopg2://{}:{}@{}:{}/{}'

CONNECTION_STRING = pg2_string.format(
        DB_USER,
        DB_PASSWORD,
        DB_HOST,
        DB_PORT,
        DB_NAME
)


#
# Tornado webapp

WEBAPP_PORT = 8888


#
# Cookie secret
COOKIE_SECRET = 'big secret'

#
# Testing
SAUCE_CONNECT = False
SAUCE_USERNAME = 'username'
SAUCE_ACCESS_KEY = 'access key'
DEFAULT_BROWSER = 'firefox::Linux'

# Allow overrides from a local config file,
# to enable test environments using the
# solar simulator and proxies for other devices

try:
    from dokomoforms.local_settings import *  # flake8: noqa
except ImportError:  # pragma: no cover
    pass
