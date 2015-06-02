"""Webapp script tests"""
import unittest

from tests.util import setUpModule, tearDownModule

import webapp

utils = (setUpModule, tearDownModule)


class TestFunctions(unittest.TestCase):
    def test_modify_text(self):
        self.assertEqual(
            webapp.modify_text('test', webapp.green),
            '\x1b[92mtest\x1b[0m'
        )
