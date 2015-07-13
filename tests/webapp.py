#!/usr/bin/env python3

"""Webapp script for testing purposes."""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from dokomoforms.options import options, parse_options
parse_options()
from dokomoforms.handlers.util import BaseHandler

from unittest.mock import patch
from webapp import main


print('FOR TESTING PURPOSES ONLY!')
print('--------------------------')
with patch.object(BaseHandler, 'get_current_user') as p:
    print('Logging in as:')
    print(options.TEST_USER)
    p.return_value = options.TEST_USER
    main()
