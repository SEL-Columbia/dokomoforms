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
def extra_fake_open(*args, **kwargs):
    yield None


@contextmanager
def fake_open_no_file(*args, **kwargs):
    raise IOError


class FakeStdout:
    flush = lambda *args, **kwargs: None

    def write(self, *args, **kwargs):
        pass


def fake_input_success(text):
    if text.startswith('D'):
        return 'y'
    return 'doko_test'


def fake_input_wrong_schema_name(text):
    if text.startswith('D'):
        return 'y'
    return 'NOT doko_test'


class FakeEngine:
    def execute(self, *args, **kwargs):
        pass

    def _run_visitor(self, *args, **kwargs):
        pass


def create_fake_engine():
    return FakeEngine()


class TestFunctions(unittest.TestCase):
    def test_modify_text(self):
        self.assertEqual(
            webapp.modify_text('test', webapp.green),
            '\x1b[92mtest\x1b[0m'
        )

    def test_get_cookie_secret(self):
        webapp.open = fake_open
        self.assertEqual(webapp.get_cookie_secret(), 'a')

    def test_get_cookie_secret_open_none(self):
        webapp.open = extra_fake_open
        self.assertRaises(AttributeError, webapp.get_cookie_secret)

    def test_get_cookie_secret_no_file(self):
        webapp.sys.stdout = FakeStdout()
        webapp.open = fake_open_no_file
        self.assertRaises(SystemExit, webapp.get_cookie_secret)

    def test_ensure_drop_schema_success(self):
        webapp.input = fake_input_success
        self.assertIsNone(
            webapp.ensure_that_user_wants_to_drop_schema()
        )

    def test_ensure_drop_schema_negative_response(self):
        webapp.input = lambda text: 'n'
        webapp.sys.stdout = FakeStdout()
        self.assertRaises(
            SystemExit,
            webapp.ensure_that_user_wants_to_drop_schema
        )

    def test_ensure_drop_schema_wrong_schema_name(self):
        webapp.input = fake_input_wrong_schema_name
        webapp.sys.stdout = FakeStdout()
        self.assertRaises(
            SystemExit,
            webapp.ensure_that_user_wants_to_drop_schema
        )


class TestApplication(unittest.TestCase):
    def test_init(self):
        webapp.options.debug = False
        webapp.options.kill = True
        webapp.create_engine = create_fake_engine
        webapp.logging.info = lambda text: None
        app = webapp.Application()
        self.assertIsNotNone(app.session)

    def test_init_no_kill(self):
        webapp.options.debug = False
        webapp.options.kill = False
        webapp.create_engine = create_fake_engine
        webapp.logging.info = lambda text: None
        app = webapp.Application()
        self.assertIsNotNone(app.session)
