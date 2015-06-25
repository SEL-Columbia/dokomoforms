"""Webapp script tests"""

import unittest
from contextlib import contextmanager

import webapp


class FakeFile:
    def read(self):
        return 'a'


@contextmanager
def fake_open(*args, **kwargs):
    yield FakeFile()


@contextmanager
def fake_open_no_file(*args, **kwargs):
    raise IOError


class FakeStdout:
    flush = lambda *args, **kwargs: None

    def write(self, *args, **kwargs):
        pass


class TestFunctions(unittest.TestCase):
    def test_modify_text(self):
        self.assertEqual(
            webapp.modify_text('test', webapp.green),
            '\x1b[92mtest\x1b[0m'
        )

    def test_get_cookie_secret(self):
        webapp.open = fake_open
        self.assertEqual(webapp.get_cookie_secret(), 'a')

    def test_get_cookie_secret_no_file(self):
        webapp.sys.stdout = FakeStdout()
        webapp.open = fake_open_no_file
        self.assertRaises(SystemExit, webapp.get_cookie_secret)
