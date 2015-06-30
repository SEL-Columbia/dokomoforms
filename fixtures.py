from dokomoforms.options import options, inject_options, parse_options

inject_options(
    schema='doko',
    #debug=True,
    # fake logged in user with ID from fixture
    TEST_USER="""
        {
            "user_id": "b7becd02-1a3f-4c1d-a0e1-286ba121aef4",
            "user_name": "test_user"
        }
    """
)
# =======
# inject_options(schema='doko_test')
parse_options()
# >>>>>>> origin/phoenix

from dokomoforms.models import create_engine, Base
from tests.fixtures import load_fixtures, unload_fixtures

engine = create_engine(echo=True)
unload_fixtures(engine, 'doko')
Base.metadata.create_all(engine)
load_fixtures(engine)
