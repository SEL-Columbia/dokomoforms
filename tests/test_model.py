"""Model tests"""
import unittest
import json

from tests.util import setUpModule, tearDownModule

from sqlalchemy.orm import sessionmaker

import dokomoforms.models as models

utils = (setUpModule, tearDownModule)

make_session = sessionmaker(bind=models.create_engine(), autocommit=True)


class TestUser(unittest.TestCase):
    def test_to_json(self):
        session = make_session()
        with session.begin():
            new_user = models.User(name='a')
            new_user.emails = [models.Email(address='b')]
            session.add(new_user)
        user = session.query(models.User).one()
        self.assertEqual(
            json.loads(user._to_json()),
            {
                'id': user.id,
                'is_active': True,
                'name': 'a',
                'emails': ['b'],
                'token_expiration': user.token_expiration.isoformat(),
                'last_update_time': user.last_update_time.isoformat(),
            }
        )
