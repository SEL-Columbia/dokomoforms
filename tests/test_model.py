"""Model tests"""
import json

from tests.util import DokoTest

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

import dokomoforms.models as models
import dokomoforms.exc as exc

make_session = sessionmaker(bind=models.create_engine(), autocommit=True)


class TestUser(DokoTest):
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


class TestSurveyNode(DokoTest):
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


class TestQuestion(DokoTest):
    def test_non_instantiable(self):
        self.assertRaises(TypeError, models.Question)


class TestChoice(DokoTest):
    def test_automatic_numbering(self):
        session = make_session()
        with session.begin():
            q = models.construct_survey_node(
                title='test_automatic_numbering',
                type_constraint='multiple_choice',
            )
            q.choices = [models.Choice(choice_text=str(i)) for i in range(3)]
            session.add(q)
        question = session.query(models.MultipleChoiceQuestion).one()
        choices = session.query(models.Choice).order_by(
            models.Choice.choice_number).all()
        self.assertEqual(question.choices, choices)
        self.assertEqual(choices[0].choice_number, 0)
        self.assertEqual(choices[1].choice_number, 1)
        self.assertEqual(choices[2].choice_number, 2)

    def test_question_delete_cascades_to_choices(self):
        session = make_session()
        with session.begin():
            q = models.construct_survey_node(
                title='test_question_delete_cascades_to_choices',
                type_constraint='multiple_choice',
            )
            q.choices = [models.Choice(choice_text='deleteme')]
            session.add(q)
        self.assertEqual(
            session.query(func.count(models.Choice.id)).scalar(),
            1
        )
        with session.begin():
            session.query(models.MultipleChoiceQuestion).delete()
        self.assertEqual(
            session.query(func.count(models.Choice.id)).scalar(),
            0
        )

    def test_wrong_question_type(self):
        session = make_session()
        with session.begin():
            q = models.construct_survey_node(
                title='test_wrong_question_type',
                type_constraint='text',
            )
            q.choices = [models.Choice(choice_text='should not show up')]
            session.add(q)
        self.assertEqual(
            session.query(func.count(models.Choice.id)).scalar(),
            0
        )
