#!/usr/bin/python

"""
This file defines configuration settings for 
running the server software.

"""

from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


# TODO: hardcoded for now, remove later
SURVEY_ID = '11e3f9b1-eb9d-47dd-8569-93b4ae10de09'

# 
# General

LOG_LEVEL = ERROR # for testing, use DEBUG in a local_settings.py file instead

#
# Database

CONNECTION_STRING = 'postgresql+psycopg2://postgres' \
                    ':thisiagreatpasswordyouguys@localhost:5432/doko'

#
# Tornado webapp

WEBAPP_PORT = 8888


#
# Cookie secret
COOKIE_SECRET = 'big secret'

#
# Testing

# Allow overrides from a local config file,
# to enable test environments using the
# solar simulator and proxies for other devices

try:
    from local_settings import *
except ImportError:
    pass

