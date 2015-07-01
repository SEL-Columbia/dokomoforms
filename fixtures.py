from dokomoforms.options import inject_options, parse_options

inject_options(
    schema='doko',
    # fake logged in user with ID from fixture
    TEST_USER="""
        {
            "user_id": "b7becd02-1a3f-4c1d-a0e1-286ba121aef4",
            "user_name": "test_user"
        }
    """
)
parse_options()

from dokomoforms.models import create_engine, Base
from tests.fixtures import load_fixtures, unload_fixtures

engine = create_engine(echo=True)
unload_fixtures(engine, 'doko')
Base.metadata.create_all(engine)
load_fixtures(engine)
