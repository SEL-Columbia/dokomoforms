#!/usr/bin/env python3
"""Webapp script for testing purposes."""
import json
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from dokomoforms.options import parse_options
parse_options()
from dokomoforms.handlers.util import BaseHandler

from unittest.mock import patch
from webapp import main, modify_text, green

try:
    from local_config import TEST_USER
except ImportError:
    print('''
    You have not specified a TEST_USER in local_config.py

    If you wish to auto-login as a certain user, set TEST_USER in
    local_config.py

    Otherwise run webapp.py as opposed to tests/python/webapp.py
    ''')
    sys.exit(1)


msg = '''
FOR TESTING PURPOSES ONLY!
FOR TESTING PURPOSES ONLY!
FOR TESTING PURPOSES ONLY!
--------------------------
Logging in as:
{}
--------------------------
FOR TESTING PURPOSES ONLY!
FOR TESTING PURPOSES ONLY!
FOR TESTING PURPOSES ONLY!
'''.format(json.dumps(TEST_USER, indent=4))
with patch.object(BaseHandler, '_current_user_cookie') as p:
    p.return_value = json.dumps(TEST_USER)
    main(modify_text(msg, green))
