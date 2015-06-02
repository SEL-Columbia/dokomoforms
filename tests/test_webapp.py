"""Webapp script tests"""
import unittest

import webapp


class TestFunctions(unittest.TestCase):
    def test_modify_text(self):
        self.assertEqual(
            webapp.modify_text('test', webapp.green),
            '\x1b[92mtest\x1b[0m'
        )
