from tests.util import setUpModule, tearDownModule  # NOQA
import unittest
import dokomoforms.models
from dokomoforms.models import Base


class TestOne(unittest.TestCase):
    def test_one(self):
        self.assertEqual(Base.metadata.schema, 'doko_test')
