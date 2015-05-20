"""Database interaction tests"""
from tests.util import setUpModule, tearDownModule
import unittest
from dokomoforms.models import Base

utils = (setUpModule, tearDownModule)


class TestSchema(unittest.TestCase):
    def test_schema_set_properly(self):
        """It took a lot of effort to make Tornado use a testing schema."""
        self.assertEqual(Base.metadata.schema, 'doko_test')
