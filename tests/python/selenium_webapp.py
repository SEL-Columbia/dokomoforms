#!/usr/bin/env python3
"""Webapp script for selenium tests."""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from dokomoforms.options import parse_options, options
parse_options()

# Override options set in config.py, local_config.py
options.port = 9999
options.schema = 'doko_test'
options.debug = True
options.demo = False
options.https = False
options.revisit_url = 'http://localhost:9999/debug/facilities'

from webapp import main
main()
