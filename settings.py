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
# Tornado webapp

WEBAPP_PORT = 8888


#
# Testing

# Allow overrides from a local config file,
# to enable test environments using the
# solar simulator and proxies for other devices

try:
    from local_settings import *
except ImportError:
    pass

