"""Database interaction tests"""
from tests.util import DokoTest

from dokomoforms.models import Base


class TestSchema(DokoTest):
    def test_schema_set_properly(self):
        """It took a lot of effort to make Tornado use a testing schema."""
        self.assertEqual(Base.metadata.schema, 'doko_test')
