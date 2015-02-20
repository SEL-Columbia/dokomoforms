#!/usr/bin/python

"""
This file defines configuration settings for 
running the server software.

"""

from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


#
# General

LOG_LEVEL = ERROR # for testing, use DEBUG in a local_settings.py file instead

#
# Database

CONNECTION_STRING = 'postgresql+psycopg2://postgres' \
                    ':password@localhost:5432/doko'

#
# Tornado webapp

WEBAPP_PORT = 8888


#
# Cookie secret
COOKIE_SECRET = 'big secret'

#
# Testing
SAUCE_USERNAME = 'username'
SAUCE_ACCESS_KEY = 'access key'
DEFAULT_BROWSER = 'firefox::Linux'

# Allow overrides from a local config file,
# to enable test environments using the
# solar simulator and proxies for other devices

try:
    from local_settings import *
except ImportError:
    pass

