"""Model tests"""
import unittest
import json

from tests.util import setUpModule, tearDownModule

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

import dokomoforms.models as models
import dokomoforms.exc as exc

utils = (setUpModule, tearDownModule)

make_session = sessionmaker(bind=models.create_engine(), autocommit=True)


class TestUser(unittest.TestCase):
    def tearDown(self):
        session = make_session()
        with session.begin():
            session.query(models.User).delete()

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

    def test_deleting_user_clears_email(self):
        session = make_session()
        with session.begin():
            new_user = models.User(name='a')
            new_user.emails = [models.Email(address='b')]
            session.add(new_user)
        self.assertEqual(
            session.query(func.count(models.Email.id)).scalar(),
            1
        )
        with session.begin():
            session.query(models.User).delete()
        self.assertEqual(
            session.query(func.count(models.Email.id)).scalar(),
            0
        )


class TestSurveyNode(unittest.TestCase):
    def tearDown(self):
        session = make_session()
        with session.begin():
            session.query(models.SurveyNode).delete()

    def test_non_instantiable(self):
        self.assertRaises(TypeError, models.SurveyNode)

    def test_construct_survey_node(self):
        session = make_session()
        with session.begin():
            session.add(models.construct_survey_node(
                type_constraint='text',
                title='test'
            ))
        sn = session.query(models.SurveyNode).one()
        self.assertEqual(sn.title, 'test')
        question = session.query(models.Question).one()
        self.assertEqual(question.title, 'test')

    def test_construct_survey_node_wrong_type(self):
        self.assertRaises(
            exc.NoSuchSurveyNodeTypeError,
            models.construct_survey_node, type_constraint='wrong'
        )

    def test_construct_survey_node_all_types(self):
        types = [
            'text', 'integer', 'decimal', 'date', 'time', 'location',
            'facility', 'multiple_choice', 'note'
        ]
        session = make_session()
        with session.begin():
            for node_type in types:
                session.add(models.construct_survey_node(
                    type_constraint=node_type,
                    title='test_' + node_type,
                ))
        self.assertEqual(
            session.query(func.count(models.SurveyNode.id)).scalar(),
            9,
        )
        self.assertEqual(
            session.query(func.count(models.Question.id)).scalar(),
            8,
        )


class TestQuestion(unittest.TestCase):

    def test_non_instantiable(self):
        self.assertRaises(TypeError, models.Question)
