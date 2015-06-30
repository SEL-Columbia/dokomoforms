"""Model tests"""

from collections import OrderedDict
import json
import datetime
from decimal import Decimal
import unittest

from tests.util import (
    DokoTest, setUpModule, tearDownModule, test_continues_after_rollback
)
utils = (setUpModule, tearDownModule)

import psycopg2

import dateutil.tz

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm.exc import FlushError

from psycopg2.extras import NumericRange, DateRange, DateTimeTZRange

import dokomoforms.models as models
import dokomoforms.models.survey
import dokomoforms.exc as exc
from dokomoforms.models.survey import Bucket


class TestBase(unittest.TestCase):
    def test_to_json(self):
        self.assertEqual(
            models.Base._to_json({'</': 'a'}),
            '{"<\\/": "a"}'
        )

        self.assertEqual(
            models.Base._to_json({'</': 'a'}, tornado_encode=False),
            '{"</": "a"}'
        )

    def test_str(self):
        self.assertEqual(
            models.Base.__str__(models.User(name='base')),
            json.dumps(
                OrderedDict((
                    ('id', None),
                    ('deleted', None),
                    ('name', 'base'),
                    ('emails', []),
                    ('role', 'enumerator'),
                    ('default_language', None),
                    ('allowed_surveys', []),
                    ('last_update_time', None),
                )),
                indent=4
            )
        )

    def test_model_json_encoder(self):
        self.assertRaises(
            TypeError, models.ModelJSONEncoder().default, object()
        )

    def test_create_engine(self):
        from dokomoforms.options import options
        engine1 = models.create_engine()
        self.assertEqual(engine1.echo, 'debug' if options.debug else False)

        engine2 = models.create_engine(True)
        self.assertEqual(engine2.echo, True)

        engine3 = models.create_engine(False)
        self.assertEqual(engine3.echo, False)


class TestUser(DokoTest):
    def test_to_json(self):
        with self.session.begin():
            new_user = models.User(name='a')
            new_user.emails = [models.Email(address='b@b')]
            self.session.add(new_user)
        user = self.session.query(models.User).one()
        self.assertEqual(
            json.loads(user._to_json(), object_pairs_hook=OrderedDict),
            OrderedDict((
                ('id', user.id),
                ('deleted', False),
                ('name', 'a'),
                ('emails', ['b@b']),
                ('role', 'enumerator'),
                ('default_language', 'English'),
                ('allowed_surveys', []),
                ('last_update_time', user.last_update_time.isoformat()),
            ))
        )

    def test_email_to_json(self):
        with self.session.begin():
            new_user = models.User(name='a')
            new_user.emails = [models.Email(address='b@b')]
            self.session.add(new_user)
        email = self.session.query(models.Email).one()
        self.assertEqual(
            email._asdict(),
            OrderedDict((
                ('id', email.id),
                ('address', 'b@b'),
                ('user', 'a'),
                ('last_update_time', email.last_update_time),
            ))
        )

    def test_survey_creator_asdict(self):
        with self.session.begin():
            new_user = models.SurveyCreator(name='a')
            new_user.emails = [models.Email(address='b@b')]
            new_user.surveys.append(
                models.Survey(title={'English': 'some title'})
            )
            self.session.add(new_user)
        user = self.session.query(models.User).one()
        self.assertEqual(
            user._asdict(),
            OrderedDict((
                ('id', user.id),
                ('deleted', False),
                ('name', 'a'),
                ('emails', ['b@b']),
                ('role', 'creator'),
                ('default_language', 'English'),
                ('allowed_surveys', []),
                ('last_update_time', user.last_update_time),
                (
                    'surveys',
                    [OrderedDict((
                        (
                            'survey_id',
                            self.session.query(models.Survey.id).scalar()
                        ),
                        ('survey_title', {'English': 'some title'}),
                    ))]
                ),
                ('token_expiration', user.token_expiration),
            ))
        )

    def test_deleting_user_clears_email(self):
        with self.session.begin():
            new_user = models.User(name='a')
            new_user.emails = [models.Email(address='b@b')]
            self.session.add(new_user)
        self.assertEqual(
            self.session.query(func.count(models.Email.id)).scalar(),
            1
        )
        with self.session.begin():
            self.session.delete(self.session.query(models.User).one())
        self.assertEqual(
            self.session.query(func.count(models.Email.id)).scalar(),
            0
        )

    def test_email_identifies_one_user(self):
        """No duplicate e-mail address allowed."""
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                user_a = models.User(name='a')
                user_a.emails = [models.Email(address='a')]
                self.session.add(user_a)

                user_b = models.User(name='b')
                user_b.emails = [models.Email(address='a')]
                self.session.add(user_b)


class TestNode(DokoTest):
    def test_non_instantiable(self):
        self.assertRaises(TypeError, models.Node)

    def test_construct_node(self):
        with self.session.begin():
            self.session.add(models.construct_node(
                type_constraint='text',
                title={'English': 'test'},
            ))
        node = self.session.query(models.Node).one()
        self.assertEqual(node.title, {'English': 'test'})
        question = self.session.query(models.Question).one()
        self.assertEqual(question.title, {'English': 'test'})

    def test_construct_node_with_languages(self):
        with self.session.begin():
            self.session.add(models.construct_node(
                type_constraint='text',
                languages=['French', 'German'],
                title={
                    'German': 'german test',
                    'Italian': 'italian test',
                    'French': 'french test',
                },
                hint={
                    'German': 'german hint ',
                    'Italian': 'italian hint',
                    'French': 'french hint',
                },
            ))
        node = self.session.query(models.Node).one()
        self.assertEqual(node.languages, ('French', 'German'))

    def test_construct_node_with_no_languages(self):
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                self.session.add(models.construct_node(
                    type_constraint='text',
                    languages=[],
                    title={
                        'German': 'german test',
                        'Italian': 'italian test',
                        'French': 'french test',
                    },
                    hint={
                        'German': 'german hint ',
                        'Italian': 'italian hint',
                        'French': 'french hint',
                    },
                ))

    def test_construct_node_with_missing_translations(self):
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                self.session.add(models.construct_node(
                    type_constraint='text',
                    languages=['French', 'German', 'Spanish'],
                    title={
                        'German': 'german test',
                        'Italian': 'italian test',
                        'French': 'french test',
                    },
                    hint={
                        'German': 'german hint ',
                        'Italian': 'italian hint',
                        'French': 'french hint',
                    },
                ))

    def test_asdict(self):
        with self.session.begin():
            self.session.add(models.construct_node(
                type_constraint='text',
                title={'English': 'test'},
            ))
        node = self.session.query(models.Node).one()
        self.assertEqual(
            node._asdict(),
            OrderedDict((
                ('id', node.id),
                ('deleted', False),
                ('languages', ('English',)),
                ('title', {'English': 'test'}),
                ('hint', {'English': ''}),
                ('allow_multiple', False),
                ('allow_other', False),
                ('type_constraint', 'text'),
                ('logic', {}),
                ('last_update_time', node.last_update_time)
            ))
        )

    def test_construct_node_wrong_type(self):
        self.assertRaises(
            exc.NoSuchNodeTypeError,
            models.construct_node, type_constraint='wrong'
        )

    def test_enforce_non_answerable(self):
        with self.assertRaises(AssertionError):
            with self.session.begin():
                creator = models.SurveyCreator(
                    name='creator',
                    surveys=[
                        models.Survey(
                            title={'English': 'non_answerable'},
                            nodes=[
                                models.construct_survey_node(
                                    answerable=False,
                                    node=models.construct_node(
                                        title={'English': 'should be note'},
                                        type_constraint='integer',
                                    ),
                                )
                            ],
                        ),
                    ],
                )
                self.session.add(creator)

    def test_enforce_answerable(self):
        with self.assertRaises(AssertionError):
            with self.session.begin():
                creator = models.SurveyCreator(
                    name='creator',
                    surveys=[
                        models.Survey(
                            title={'English': 'answerable'},
                            nodes=[
                                models.construct_survey_node(
                                    answerable=True,
                                    node=models.construct_node(
                                        title={
                                            'English': 'should be question'
                                        },
                                        type_constraint='note',
                                    ),
                                )
                            ],
                        ),
                    ],
                )
                self.session.add(creator)

    def test_construct_node_all_types(self):
        with self.session.begin():
            for node_type in models.NODE_TYPES:
                self.session.add(models.construct_node(
                    type_constraint=node_type,
                    title={'English': 'test_' + node_type},
                ))
        self.assertEqual(
            self.session.query(func.count(models.Node.id)).scalar(),
            11,
        )
        self.assertEqual(
            self.session.query(func.count(models.Note.id)).scalar(),
            1,
        )
        self.assertEqual(
            self.session.query(func.count(models.Question.id)).scalar(),
            10,
        )

    def test_note_asdict(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=False,
                        node=models.construct_node(
                            type_constraint='note',
                            title={'English': 'a note'},
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        note = self.session.query(models.Node).one()
        self.assertEqual(
            note._asdict(),
            OrderedDict((
                ('id', note.id),
                ('deleted', False),
                ('languages', ('English',)),
                ('title', {'English': 'a note'}),
                ('type_constraint', 'note'),
                ('logic', {}),
                ('last_update_time', note.last_update_time),
            ))
        )

    def test_multiple_choice_question_asdict(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='multiple_choice',
                            title={
                                'English': 'mc question',
                                'German': 'German',
                                'French': 'French',
                            },
                            choices=[
                                models.Choice(
                                    choice_text={
                                        'English': 'one',
                                        'German': 'German choice',
                                        'French': 'French choice',
                                    },
                                ),
                            ],
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        question = self.session.query(models.Node).one()
        self.assertEqual(
            question._asdict(),
            OrderedDict((
                ('id', question.id),
                ('deleted', False),
                (
                    'title',
                    OrderedDict((
                        ('English', 'mc question'),
                        ('French', 'French'),
                        ('German', 'German'),
                    ))
                ),
                ('hint', {'English': ''}),
                (
                    'choices',
                    [OrderedDict((
                        ('choice_id', question.choices[0].id),
                        (
                            'choice_text',
                            OrderedDict((
                                ('English', 'one'),
                                ('French', 'French choice'),
                                ('German', 'German choice'),
                            ))
                        ),
                    ))]
                ),
                ('allow_multiple', False),
                ('allow_other', False),
                ('type_constraint', 'multiple_choice'),
                ('logic', {}),
                ('last_update_time', question.last_update_time),
            ))
        )


class TestQuestion(DokoTest):
    def test_non_instantiable(self):
        self.assertRaises(TypeError, models.Question)


class TestChoice(DokoTest):
    def test_automatic_numbering(self):
        with self.session.begin():
            q = models.construct_node(
                title={'English': 'test_automatic_numbering'},
                type_constraint='multiple_choice',
            )
            q.choices = [models.Choice(choice_text={
                'English': str(i)
            }) for i in range(3)]
            self.session.add(q)
        question = self.session.query(models.MultipleChoiceQuestion).one()
        choices = self.session.query(models.Choice).order_by(
            models.Choice.choice_number).all()
        self.assertEqual(question.choices, choices)
        self.assertEqual(choices[0].choice_number, 0)
        self.assertEqual(choices[1].choice_number, 1)
        self.assertEqual(choices[2].choice_number, 2)

    def test_asdict(self):
        with self.session.begin():
            q = models.construct_node(
                title={'English': 'some MC question'},
                type_constraint='multiple_choice',
            )
            q.choices = [models.Choice(choice_text={'English': 'some choice'})]
            self.session.add(q)

        choice = self.session.query(models.Choice).one()
        self.assertEqual(
            choice._asdict(),
            OrderedDict((
                ('id', choice.id),
                ('deleted', False),
                ('choice_text', OrderedDict((('English', 'some choice'),))),
                ('choice_number', 0),
                (
                    'question',
                    OrderedDict((
                        ('question_id', choice.question_id),
                        (
                            'question_title',
                            OrderedDict((
                                ('English', 'some MC question'),
                            ))
                        ),
                    ))
                ),
                ('last_update_time', choice.last_update_time),
            ))
        )

    def test_question_delete_cascades_to_choices(self):
        with self.session.begin():
            q = models.construct_node(
                title={'English': 'test_question_delete_cascades_to_choices'},
                type_constraint='multiple_choice',
            )
            q.choices = [models.Choice(choice_text={'English': 'deleteme'})]
            self.session.add(q)
        self.assertEqual(
            self.session.query(func.count(models.Choice.id)).scalar(),
            1
        )
        with self.session.begin():
            self.session.delete(
                self.session.query(models.MultipleChoiceQuestion).one()
            )
        self.assertEqual(
            self.session.query(func.count(models.Choice.id)).scalar(),
            0
        )

    def test_wrong_question_type(self):
        with self.session.begin():
            q = models.construct_node(
                title={'English': 'test_wrong_question_type'},
                type_constraint='text',
            )
            q.choices = [models.Choice(choice_text='should not show up')]
            self.session.add(q)
        self.assertEqual(
            self.session.query(func.count(models.Choice.id)).scalar(),
            0
        )


class TestSurvey(DokoTest):
    def test_set_tzinfos(self):
        from dokomoforms.models.survey import _set_tzinfos
        _set_tzinfos()
        from dokomoforms.models.survey import TZINFOS
        self.assertIsNotNone(TZINFOS)

    def test_one_node_surveys(self):
        number_of_questions = 11
        with self.session.begin():
            creator = models.SurveyCreator(
                name='creator',
                emails=[models.Email(address='email@email')],
            )
            node_types = list(models.NODE_TYPES)
            for node_type in node_types:
                survey = models.Survey(
                    title={'English': node_type + '_survey'},
                    nodes=[
                        models.construct_survey_node(
                            answerable=node_type != 'note',
                            node=models.construct_node(
                                type_constraint=node_type,
                                title={'English': node_type + '_node'},
                            ),
                        ),
                    ],
                )
                creator.surveys.append(survey)
            self.session.add(creator)

        the_creator = self.session.query(models.SurveyCreator).one()
        self.assertEqual(
            len(the_creator.surveys),
            number_of_questions,
            msg='not all {} surveys were created'.format(number_of_questions)
        )
        self.assertListEqual(
            [the_creator.surveys[n].nodes[0].type_constraint
                for n in range(number_of_questions)],
            node_types,
            msg='the surveys were not created in the right order'
        )
        self.assertListEqual(
            [len(the_creator.surveys[n].nodes)
                for n in range(number_of_questions)],
            [1] * number_of_questions,
            msg='there is a survey with more than one node'
        )

    def test_asdict(self):
        with self.session.begin():
            creator = models.SurveyCreator(
                name='creator',
                emails=[models.Email(address='email@email')],
            )
            survey = models.Survey(
                title={'English': 'some survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'integer node'},
                        ),
                    ),
                ],
            )
            creator.surveys.append(survey)
            self.session.add(creator)

        the_survey = self.session.query(models.Survey).one()
        self.assertEqual(
            the_survey._asdict(),
            OrderedDict((
                ('id', the_survey.id),
                ('deleted', False),
                ('title', OrderedDict((('English', 'some survey'),))),
                ('default_language', 'English'),
                ('survey_type', 'public'),
                ('version', 1),
                (
                    'creator_id',
                    self.session.query(models.SurveyCreator.id).scalar()
                ),
                ('creator_name', 'creator'),
                ('metadata', {}),
                ('created_on', the_survey.created_on),
                ('last_update_time', the_survey.last_update_time),
                ('nodes', [self.session.query(models.SurveyNode).one()]),
            ))
        )

    def test_title_in_default_langauge_must_exist(self):
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                creator = models.SurveyCreator(
                    name='creator',
                    surveys=[
                        models.Survey(
                            title={'French': 'answerable'},
                        ),
                    ],
                )
                self.session.add(creator)

    def test_title_in_default_langauge_must_not_be_empty(self):
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                creator = models.SurveyCreator(
                    name='creator',
                    surveys=[
                        models.Survey(
                            title={'English': ''},
                        ),
                    ],
                )
                self.session.add(creator)

    def test_alternate_default_langauge(self):
        with self.session.begin():
            creator = models.SurveyCreator(
                name='creator',
                surveys=[
                    models.Survey(
                        title={'French': 'answerable'},
                        languages=['French'],
                        default_language='French',
                    ),
                ],
            )
            self.session.add(creator)

        self.assertEqual(
            self.session.query(func.count(models.Survey.id)).scalar(),
            1
        )


class TestSurveyNode(DokoTest):
    def test_requested_translations_must_exist(self):
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                creator = models.SurveyCreator(
                    name='creator',
                    emails=[models.Email(address='email@email')],
                    surveys=[
                        models.Survey(
                            title={'French': 'french title'},
                            languages=['French'],
                            default_language='French',
                            nodes=[
                                models.construct_survey_node(
                                    answerable=True,
                                    node=models.construct_node(
                                        type_constraint='integer',
                                        languages=['German'],
                                        title={'German': 'german title'},
                                        hint={'German': ''},
                                    ),
                                ),
                            ],
                        ),
                    ],
                )
                self.session.add(creator)

    def test_requested_translations_must_exist_even_nested(self):
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                super_nested = models.construct_node(
                    type_constraint='text',
                    languages=['German'],
                    title={'German': 'german question'},
                    hint={'German': ''},
                )
                creator = models.SurveyCreator(
                    name='creator',
                    emails=[models.Email(address='email@email')],
                    surveys=[
                        models.Survey(
                            title={'French': 'french title'},
                            languages=['French'],
                            default_language='French',
                            nodes=[
                                models.construct_survey_node(
                                    answerable=True,
                                    node=models.construct_node(
                                        type_constraint='integer',
                                        languages=['French'],
                                        title={'French': 'French question'},
                                        hint={'French': ''},
                                    ),
                                    sub_surveys=[
                                        models.SubSurvey(
                                            buckets=[
                                                models.construct_bucket(
                                                    bucket_type='integer',
                                                    bucket='[2, 5]',
                                                ),
                                            ],
                                            nodes=[
                                                models.construct_survey_node(
                                                    answerable=True,
                                                    node=super_nested,
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                )
                self.session.add(creator)

    def test_super_nested(self):
        with self.session.begin():
            super_nested = models.construct_node(
                type_constraint='text',
                languages=['French'],
                title={'French': 'french question'},
                hint={'French': ''},
            )
            creator = models.SurveyCreator(
                name='creator',
                emails=[models.Email(address='email@email')],
                surveys=[
                    models.Survey(
                        title={'French': 'french title'},
                        languages=['French'],
                        default_language='French',
                        nodes=[
                            models.construct_survey_node(
                                answerable=True,
                                node=models.construct_node(
                                    type_constraint='integer',
                                    languages=['French'],
                                    title={'French': 'French question'},
                                    hint={'French': ''},
                                ),
                                sub_surveys=[
                                    models.SubSurvey(
                                        buckets=[
                                            models.construct_bucket(
                                                bucket_type='integer',
                                                bucket='[2, 5]',
                                            ),
                                        ],
                                        nodes=[
                                            models.construct_survey_node(
                                                answerable=True,
                                                node=super_nested,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            )
            self.session.add(creator)

        self.assertEqual(
            self.session.query(func.count(models.Survey.id)).scalar(),
            1
        )
        self.assertEqual(
            self.session.query(func.count(models.Node.id)).scalar(),
            2
        )

    def test_asdict(self):
        with self.session.begin():
            creator = models.SurveyCreator(
                name='creator',
                emails=[models.Email(address='email@email')],
            )
            survey = models.Survey(
                title={'English': 'some survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'integer node'},
                        ),
                    ),
                ],
            )
            creator.surveys.append(survey)
            self.session.add(creator)

        survey_node = self.session.query(models.SurveyNode).one()
        self.assertEqual(
            survey_node._asdict(),
            OrderedDict((
                ('deleted', False),
                ('languages', ('English',)),
                ('title', {'English': 'integer node'}),
                ('hint', {'English': ''}),
                ('allow_multiple', False),
                ('allow_other', False),
                ('type_constraint', 'integer'),
                ('logic', {}),
                ('last_update_time', survey_node.last_update_time),
                ('node_id', self.session.query(models.Node.id).scalar()),
                ('id', survey_node.id),
                ('required', False),
                ('allow_dont_know', False),
            ))
        )

    def test_asdict_with_sub_survey(self):
        with self.session.begin():
            creator = models.SurveyCreator(
                name='creator',
                emails=[models.Email(address='email@email')],
            )
            survey = models.Survey(
                title={'English': 'some survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'integer node'},
                        ),
                        sub_surveys=[
                            models.SubSurvey(),
                        ],
                    ),
                ],
            )
            creator.surveys.append(survey)
            self.session.add(creator)

        survey_node = self.session.query(models.SurveyNode).one()
        self.assertEqual(
            survey_node._asdict(),
            OrderedDict((
                ('deleted', False),
                ('languages', ('English',)),
                ('title', {'English': 'integer node'}),
                ('hint', {'English': ''}),
                ('allow_multiple', False),
                ('allow_other', False),
                ('type_constraint', 'integer'),
                ('logic', {}),
                ('last_update_time', survey_node.last_update_time),
                ('node_id', self.session.query(models.Node.id).scalar()),
                ('id', survey_node.id),
                ('required', False),
                ('allow_dont_know', False),
                ('sub_surveys', self.session.query(models.SubSurvey).all()),
            ))
        )

    def test_super_nested_to_json(self):
        with self.session.begin():
            super_nested = models.construct_node(
                type_constraint='text',
                languages=['French'],
                title={'French': 'French question'},
                hint={'French': ''},
            )
            creator = models.SurveyCreator(
                name='creator',
                emails=[models.Email(address='email@email')],
                surveys=[
                    models.Survey(
                        title={'French': 'french title'},
                        languages=['French'],
                        default_language='French',
                        nodes=[
                            models.construct_survey_node(
                                answerable=True,
                                node=models.construct_node(
                                    type_constraint='integer',
                                    languages=['French'],
                                    title={'French': 'French question'},
                                    hint={'French': ''},
                                ),
                                sub_surveys=[
                                    models.SubSurvey(
                                        buckets=[
                                            models.construct_bucket(
                                                bucket_type='integer',
                                                bucket='[2, 5]',
                                            ),
                                        ],
                                        nodes=[
                                            models.construct_survey_node(
                                                answerable=True,
                                                node=super_nested,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            )
            self.session.add(creator)

        survey = self.session.query(models.Survey).one()
        integer_question = (
            self.session
            .query(models.Question)
            .filter_by(type_constraint='integer')
            .one()
        )
        n = (
            self.session
            .query(models.Question)
            .filter_by(type_constraint='text')
            .one()
        )
        n_t = n.last_update_time.isoformat()
        n_i = n.id
        self.assertEqual(
            json.loads(survey._to_json(), object_pairs_hook=OrderedDict),
            OrderedDict((
                ('id', survey.id),
                ('deleted', False),
                ('title', OrderedDict((('French', 'french title'),))),
                ('default_language', 'French'),
                ('survey_type', 'public'),
                ('version', 1),
                ('creator_id', self.session.query(models.User.id).scalar()),
                ('creator_name', 'creator'),
                ('metadata', OrderedDict()),
                ('created_on', survey.created_on.isoformat()),
                ('last_update_time', survey.last_update_time.isoformat()),
                (
                    'nodes',
                    [
                        OrderedDict((
                            ('deleted', False),
                            ('languages', ['French']),
                            (
                                'title',
                                OrderedDict((('French', 'French question'),))
                            ),
                            ('hint', OrderedDict((('French', ''),))),
                            ('allow_multiple', False),
                            ('allow_other', False),
                            ('type_constraint', 'integer'),
                            ('logic', OrderedDict()),
                            (
                                'last_update_time',
                                integer_question.last_update_time.isoformat()
                            ),
                            ('node_id', integer_question.id),
                            (
                                'id',
                                self.session
                                .query(models.SurveyNode.id)
                                .filter_by(type_constraint='integer')
                                .scalar()
                            ),
                            ('required', False),
                            ('allow_dont_know', False),
                            (
                                'sub_surveys',
                                [
                                    OrderedDict((
                                        ('deleted', False),
                                        ('buckets', ['[2,6)']),
                                        ('repeatable', False),
                                        (
                                            'nodes',
                                            [
                                                OrderedDict((
                                                    ('deleted', False),
                                                    ('languages', ['French']),
                                                    (
                                                        'title',
                                                        OrderedDict((
                                                            (
                                                                'French',
                                                                'French'
                                                                ' question'
                                                            ),
                                                        ))
                                                    ),
                                                    (
                                                        'hint',
                                                        OrderedDict((
                                                            ('French', ''),
                                                        ))
                                                    ),
                                                    ('allow_multiple', False),
                                                    ('allow_other', False),
                                                    (
                                                        'type_constraint',
                                                        'text'
                                                    ),
                                                    ('logic', OrderedDict()),
                                                    ('last_update_time', n_t),
                                                    ('node_id', n_i),
                                                    (
                                                        'id',
                                                        self.session
                                                        .query(
                                                            models.SurveyNode
                                                            .id
                                                        )
                                                        .filter_by(
                                                            type_constraint=(
                                                                'text'
                                                            )
                                                        )
                                                        .scalar()
                                                    ),
                                                    ('required', False),
                                                    (
                                                        'allow_dont_know',
                                                        False
                                                    ),
                                                ))
                                            ]
                                        ),
                                    ))
                                ]
                            ),
                        ))
                    ]
                ),
            ))
        )


class TestBucket(DokoTest):
    def _create_blank_survey(self) -> (models.SurveyCreator, models.Survey):
        creator = models.SurveyCreator(
            name='creator',
            emails=[models.Email(address='email@email')],
        )
        survey = models.Survey(title={'English': 'TestBucket'})
        creator.surveys = [survey]
        return creator, survey

    def test_bucket(self):
        self.assertRaises(TypeError, Bucket.bucket)

    def test_non_instantiable(self):
        self.assertRaises(TypeError, Bucket)

    def test_bucket_type_exists(self):
        self.assertRaises(
            exc.NoSuchBucketTypeError,
            models.construct_bucket,
            bucket_type='wrong',
        )

    def test_integer_bucket(self):
        with self.session.begin():
            creator, survey = self._create_blank_survey()
            survey.nodes = [
                models.construct_survey_node(
                    answerable=True,
                    node=models.construct_node(
                        type_constraint='integer',
                        title={'English': 'node'},
                    ),
                    sub_surveys=[
                        models.SubSurvey(
                            buckets=[
                                models.construct_bucket(
                                    bucket_type='integer',
                                    bucket='(1, 2]'
                                ),
                            ],
                        ),
                    ],
                ),
            ]
            self.session.add(creator)

        the_bucket = self.session.query(Bucket).one()
        self.assertEqual(the_bucket.bucket, NumericRange(2, 3, '[)'))

    def test_sub_survey_asdict(self):
        with self.session.begin():
            creator, survey = self._create_blank_survey()
            survey.nodes = [
                models.construct_survey_node(
                    answerable=True,
                    node=models.construct_node(
                        type_constraint='integer',
                        title={'English': 'node'},
                    ),
                    sub_surveys=[
                        models.SubSurvey(
                            buckets=[
                                models.construct_bucket(
                                    bucket_type='integer',
                                    bucket='(1, 2]'
                                ),
                            ],
                        ),
                    ],
                ),
            ]
            self.session.add(creator)

        sub_survey = self.session.query(models.SubSurvey).one()
        self.assertEqual(
            sub_survey._asdict(),
            OrderedDict((
                ('deleted', False),
                ('buckets', [NumericRange(2, 3, '[)')]),
                ('repeatable', False),
                ('nodes', []),
            ))
        )

    def test_bucket_asdict(self):
        with self.session.begin():
            creator, survey = self._create_blank_survey()
            survey.nodes = [
                models.construct_survey_node(
                    answerable=True,
                    node=models.construct_node(
                        type_constraint='integer',
                        title={'English': 'node'},
                    ),
                    sub_surveys=[
                        models.SubSurvey(
                            buckets=[
                                models.construct_bucket(
                                    bucket_type='integer',
                                    bucket='(1, 2]'
                                ),
                            ],
                        ),
                    ],
                ),
            ]
            self.session.add(creator)

        bucket = self.session.query(Bucket).one()
        self.assertEqual(
            bucket._asdict(),
            OrderedDict((
                ('id', bucket.id),
                ('bucket_type', 'integer'),
                ('bucket', NumericRange(2, 3, '[)')),
            ))
        )

    def test_integer_incorrect_bucket_type(self):
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                creator, survey = self._create_blank_survey()
                survey.nodes = [
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'node'},
                        ),
                        sub_surveys=[
                            models.SubSurvey(
                                buckets=[
                                    models.construct_bucket(
                                        bucket_type='decimal',
                                        bucket='(1.3, 2.3]'
                                    ),
                                ],
                            ),
                        ],
                    ),
                ]
                self.session.add(creator)

    def test_integer_incorrect_range(self):
        """A decimal is not an integer"""
        with self.assertRaises(DataError):
            with self.session.begin():
                creator, survey = self._create_blank_survey()
                survey.nodes = [
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'node'},
                        ),
                        sub_surveys=[
                            models.SubSurvey(
                                buckets=[
                                    models.construct_bucket(
                                        bucket_type='integer',
                                        bucket='(1.3, 2.3]'
                                    ),
                                ],
                            ),
                        ],
                    ),
                ]
                self.session.add(creator)

    def test_integer_two_buckets(self):
        with self.session.begin():
            creator, survey = self._create_blank_survey()
            survey.nodes = [
                models.construct_survey_node(
                    answerable=True,
                    node=models.construct_node(
                        type_constraint='integer',
                        title={'English': 'node'},
                    ),
                    sub_surveys=[
                        models.SubSurvey(
                            buckets=[
                                models.construct_bucket(
                                    bucket_type='integer',
                                    bucket='(1, 2]'
                                ),
                                models.construct_bucket(
                                    bucket_type='integer',
                                    bucket='(4, 6]'
                                ),
                            ],
                        ),
                    ],
                ),
            ]
            self.session.add(creator)

        self.assertEqual(self.session.query(func.count(Bucket.id)).scalar(), 2)

    def test_integer_bucket_no_overlap(self):
        """The range [,] covers all integers, so (-2, 6] overlaps."""
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                creator, survey = self._create_blank_survey()
                survey.nodes = [
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'node'},
                        ),
                        sub_surveys=[
                            models.SubSurvey(
                                buckets=[
                                    models.construct_bucket(
                                        bucket_type='integer',
                                        bucket='[,]'
                                    ),
                                    models.construct_bucket(
                                        bucket_type='integer',
                                        bucket='(-2, 6]'
                                    ),
                                ],
                            ),
                        ],
                    ),
                ]
                self.session.add(creator)

    def test_integer_bucket_no_overlap_different_sub_surveys(self):
        """
        Different SubSurveys belonging to the same SurveyNode cannot have
        overlapping buckets.
        """
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                creator, survey = self._create_blank_survey()
                survey.nodes = [
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'node'},
                        ),
                        sub_surveys=[
                            models.SubSurvey(
                                buckets=[
                                    models.construct_bucket(
                                        bucket_type='integer',
                                        bucket='[1, 5]'
                                    ),
                                ],
                            ),
                            models.SubSurvey(
                                buckets=[
                                    models.construct_bucket(
                                        bucket_type='integer',
                                        bucket='[3, 7]'
                                    ),
                                ],
                            ),
                        ],
                    ),
                ]
                self.session.add(creator)

    def test_integer_bucket_no_empty_range(self):
        """There are no integers between 2 and 3 exclusive"""
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                creator, survey = self._create_blank_survey()
                survey.nodes = [
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'node'},
                        ),
                        sub_surveys=[
                            models.SubSurvey(
                                buckets=[
                                    models.construct_bucket(
                                        bucket_type='integer',
                                        bucket='(2, 3)'
                                    ),
                                ],
                            ),
                        ],
                    ),
                ]
                self.session.add(creator)

    def test_integer_overlapping_buckets_different_nodes(self):
        """Nothing wrong with overlapping buckets on different nodes."""
        with self.session.begin():
            creator, survey = self._create_blank_survey()
            survey.nodes = [
                models.construct_survey_node(
                    answerable=True,
                    node=models.construct_node(
                        type_constraint='integer',
                        title={'English': 'node1'},
                    ),
                    sub_surveys=[
                        models.SubSurvey(
                            buckets=[
                                models.construct_bucket(
                                    bucket_type='integer',
                                    bucket='[1, 5]'
                                ),
                            ],
                        ),
                    ],
                ),
                models.construct_survey_node(
                    answerable=True,
                    node=models.construct_node(
                        type_constraint='integer',
                        title={'English': 'node2'},
                    ),
                    sub_surveys=[
                        models.SubSurvey(
                            buckets=[
                                models.construct_bucket(
                                    bucket_type='integer',
                                    bucket='[3, 7]'
                                ),
                            ],
                        ),
                    ],
                ),
            ]
            self.session.add(creator)

        self.assertEqual(self.session.query(func.count(Bucket.id)).scalar(), 2)

    def test_decimal_bucket(self):
        with self.session.begin():
            creator, survey = self._create_blank_survey()
            survey.nodes = [
                models.construct_survey_node(
                    answerable=True,
                    node=models.construct_node(
                        type_constraint='decimal',
                        title={'English': 'node'},
                    ),
                    sub_surveys=[
                        models.SubSurvey(
                            buckets=[
                                models.construct_bucket(
                                    bucket_type='decimal',
                                    bucket='(1.3, 2.3]'
                                ),
                            ],
                        ),
                    ],
                ),
            ]
            self.session.add(creator)

        the_bucket = self.session.query(Bucket).one()
        self.assertEqual(
            the_bucket.bucket,
            NumericRange(Decimal('1.3'), Decimal('2.3'), '(]'),
        )

    def test_date_bucket(self):
        with self.session.begin():
            creator, survey = self._create_blank_survey()
            survey.nodes = [
                models.construct_survey_node(
                    answerable=True,
                    node=models.construct_node(
                        type_constraint='date',
                        title={'English': 'node'},
                    ),
                    sub_surveys=[
                        models.SubSurvey(
                            buckets=[
                                models.construct_bucket(
                                    bucket_type='date',
                                    bucket='(2015-1-1, 2015-2-2]'
                                ),
                            ],
                        ),
                    ],
                ),
            ]
            self.session.add(creator)

        the_bucket = self.session.query(Bucket).one()
        self.assertEqual(
            the_bucket.bucket,
            DateRange(
                datetime.date(2015, 1, 2), datetime.date(2015, 2, 3), '[)'
            ),
        )

    def test_time_bucket(self):
        with self.session.begin():
            creator, survey = self._create_blank_survey()
            survey.nodes = [
                models.construct_survey_node(
                    answerable=True,
                    node=models.construct_node(
                        type_constraint='time',
                        title={'English': 'node'},
                    ),
                    sub_surveys=[
                        models.SubSurvey(
                            buckets=[
                                models.construct_bucket(
                                    bucket_type='time',
                                    bucket='(1:11, 2:22]'
                                ),
                            ],
                        ),
                    ],
                ),
            ]
            self.session.add(creator)

        the_bucket = self.session.query(Bucket).one()
        tzinfo = the_bucket.bucket.lower.tzinfo
        self.assertEqual(
            the_bucket.bucket,
            DateTimeTZRange(
                datetime.datetime(1970, 1, 1, 1, 11, tzinfo=tzinfo),
                datetime.datetime(1970, 1, 1, 2, 22, tzinfo=tzinfo),
                '(]'
            )
        )

    def test_set_time_bucket_dates(self):
        _set_dates = dokomoforms.models.survey._set_time_bucket_dates
        self.assertEqual(
            _set_dates('   (  04:05:06.789-8  , 04:05:06.790-8   ]'),
            '(1970-01-01T04:05:06.789000-08:00,'
            '1970-01-01T04:05:06.790000-08:00]'
        )

    def test_time_bucket_all_valid_time_formats(self):
        valid_time_formats = [
            # From
            # http://www.postgresql.org/docs/9.4/static/datatype-datetime.html
            # #DATATYPE-DATETIME-TIME-TABLE
            '[04:05:06.789, 04:05:06.790]',
            '[04:05:06, 04:05:07]',
            '[04:05, 04:06]',
            # This gets interpreted as a date -- no go
            # '[040506, 040507]',
            '[04:05 AM, 04:06 AM]',
            '[04:05 PM, 04:06 PM]',
            '[04:05:06.789-8, 04:05:06.790-8]',
            '[04:05:06-08:00, 04:05:07-08:00]',
            '[04:05-08:00, 04:06-08:00]',
            # This gets interpreted as a date plus an hour
            # '[040506-08, 040507-08]',
            '[04:05:06 PST, 04:05:07 PST]',
            # Not sure if this is worth trying to parse...
            # '[2003-04-12 04:05:06 America/New_York,'
            # ' 2003-04-12 04:05:07 America/New_York]',
            '[,04:05 AM]',
            '[04:05 AM,]',
            '[,]',
        ]
        with self.session.begin():
            creator = models.SurveyCreator(
                name='creator',
                emails=[models.Email(address='email@email')],
            )
            for i, time_format in enumerate(valid_time_formats):
                survey = models.Survey(
                    title={'English': 'Test {}'.format(i)}
                )
                creator.surveys.append(survey)
                survey.nodes = [
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='time',
                            title={'English': 'node'},
                        ),
                        sub_surveys=[
                            models.SubSurvey(
                                buckets=[
                                    models.construct_bucket(
                                        bucket_type='time',
                                        bucket=time_format
                                    ),
                                ],
                            ),
                        ],
                    ),
                ]
            self.session.add(creator)

        self.assertEqual(
            self.session.query(func.count(Bucket.id)).scalar(),
            12
        )
        buckets = self.session.query(Bucket)
        tzinfo = buckets[0].bucket.lower.tzinfo

        def make_range(lower: tuple, upper: tuple) -> DateTimeTZRange:
            return DateTimeTZRange(
                datetime.datetime(*lower, tzinfo=tzinfo),
                datetime.datetime(*upper, tzinfo=tzinfo),
                '[]'
            )

        self.assertEqual(
            buckets[0].bucket,
            make_range(
                (1970, 1, 1, 4, 5, 6, 789000), (1970, 1, 1, 4, 5, 6, 790000)
            )
        )
        self.assertEqual(
            buckets[1].bucket,
            make_range(
                (1970, 1, 1, 4, 5, 6), (1970, 1, 1, 4, 5, 7)
            )
        )
        self.assertEqual(
            buckets[2].bucket,
            make_range(
                (1970, 1, 1, 4, 5), (1970, 1, 1, 4, 6)
            )
        )
        self.assertEqual(
            buckets[3].bucket,
            make_range(
                (1970, 1, 1, 4, 5), (1970, 1, 1, 4, 6)
            )
        )
        self.assertEqual(
            buckets[4].bucket,
            make_range(
                (1970, 1, 1, 16, 5), (1970, 1, 1, 16, 6)
            )
        )
        specified_tz = psycopg2.tz.FixedOffsetTimezone(offset=-300, name=None)
        self.assertEqual(
            buckets[5].bucket,
            DateTimeTZRange(
                datetime.datetime(
                    1970, 1, 1, 7, 5, 6, 789000, tzinfo=specified_tz
                ),
                datetime.datetime(
                    1970, 1, 1, 7, 5, 6, 790000, tzinfo=specified_tz
                ),
                '[]'
            )
        )
        self.assertEqual(
            buckets[6].bucket,
            DateTimeTZRange(
                datetime.datetime(
                    1970, 1, 1, 7, 5, 6, tzinfo=specified_tz
                ),
                datetime.datetime(
                    1970, 1, 1, 7, 5, 7, tzinfo=specified_tz
                ),
                '[]'
            )
        )
        self.assertEqual(
            buckets[7].bucket,
            DateTimeTZRange(
                datetime.datetime(
                    1970, 1, 1, 7, 5, tzinfo=specified_tz
                ),
                datetime.datetime(
                    1970, 1, 1, 7, 6, tzinfo=specified_tz
                ),
                '[]'
            )
        )
        self.assertEqual(
            buckets[8].bucket,
            DateTimeTZRange(
                datetime.datetime(
                    1970, 1, 1, 7, 5, 6, tzinfo=specified_tz
                ),
                datetime.datetime(
                    1970, 1, 1, 7, 5, 7, tzinfo=specified_tz
                ),
                '[]'
            )
        )
        self.assertEqual(
            buckets[9].bucket,
            make_range(
                (1970, 1, 1, 0, 0), (1970, 1, 1, 4, 5)
            )
        )
        self.assertEqual(
            buckets[10].bucket,
            make_range(
                (1970, 1, 1, 4, 5), (1970, 1, 2, 0, 0)
            )
        )
        self.assertEqual(
            buckets[11].bucket,
            make_range(
                (1970, 1, 1, 0, 0), (1970, 1, 2, 0, 0)
            )
        )

    def test_timestamp_bucket(self):
        with self.session.begin():
            creator, survey = self._create_blank_survey()
            survey.nodes = [
                models.construct_survey_node(
                    answerable=True,
                    node=models.construct_node(
                        type_constraint='timestamp',
                        title={'English': 'node'},
                    ),
                    sub_surveys=[
                        models.SubSurvey(
                            buckets=[
                                models.construct_bucket(
                                    bucket_type='timestamp',
                                    bucket='(2015-1-1 1:11, 2015-1-1 2:22]'
                                ),
                            ],
                        ),
                    ],
                ),
            ]
            self.session.add(creator)

        the_bucket = self.session.query(Bucket).one()
        tzinfo = the_bucket.bucket.lower.tzinfo
        self.assertEqual(
            the_bucket.bucket,
            DateTimeTZRange(
                datetime.datetime(2015, 1, 1, 1, 11, tzinfo=tzinfo),
                datetime.datetime(2015, 1, 1, 2, 22, tzinfo=tzinfo),
                '(]'
            )
        )

    def test_multiple_choice_bucket(self):
        with self.session.begin():
            creator, survey = self._create_blank_survey()
            node = models.construct_node(
                type_constraint='multiple_choice',
                title={'English': 'node'},
            )
            choice = models.Choice(choice_text={'English': ''})
            node.choices = [choice]

            survey.nodes = [
                models.construct_survey_node(
                    answerable=True,
                    node=node,
                    sub_surveys=[
                        models.SubSurvey(
                            buckets=[
                                models.construct_bucket(
                                    bucket_type='multiple_choice',
                                    bucket=choice,
                                ),
                            ],
                        ),
                    ]
                ),
            ]
            self.session.add(creator)

        the_bucket = self.session.query(Bucket).one()
        the_choice = self.session.query(models.Choice).one()
        self.assertIs(the_bucket.bucket, the_choice)

    def test_multiple_choice_multiple_buckets(self):
        with self.session.begin():
            creator, survey = self._create_blank_survey()
            node = models.construct_node(
                type_constraint='multiple_choice',
                title={'English': 'node'},
            )
            choice1 = models.Choice(choice_text={'English': ''})
            choice2 = models.Choice(choice_text={'English': 'second choice'})
            node.choices = [choice1, choice2]

            survey.nodes = [
                models.construct_survey_node(
                    answerable=True,
                    node=node,
                    sub_surveys=[
                        models.SubSurvey(
                            buckets=[
                                models.construct_bucket(
                                    bucket_type='multiple_choice',
                                    bucket=choice1
                                ),
                                models.construct_bucket(
                                    bucket_type='multiple_choice',
                                    bucket=choice2
                                ),
                            ],
                        ),
                    ]
                ),
            ]
            self.session.add(creator)

        bucket1 = self.session.query(Bucket).all()[0]
        choice1 = self.session.query(models.Choice).all()[0]
        self.assertIs(bucket1.bucket, choice1)

        bucket2 = self.session.query(Bucket).all()[1]
        choice2 = self.session.query(models.Choice).all()[1]
        self.assertIs(bucket2.bucket, choice2)

    def test_multiple_choice_bucket_no_overlap(self):
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                creator, survey = self._create_blank_survey()
                node = models.construct_node(
                    type_constraint='multiple_choice', title='node'
                )
                choice = models.Choice()
                node.choices = [choice]

                survey.nodes = [
                    models.construct_survey_node(
                        answerable=True,
                        node=node,
                        sub_surveys=[
                            models.SubSurvey(
                                buckets=[
                                    models.construct_bucket(
                                        bucket_type='multiple_choice',
                                        bucket=choice
                                    ),
                                    models.construct_bucket(
                                        bucket_type='multiple_choice',
                                        bucket=choice
                                    ),
                                ],
                            ),
                        ]
                    ),
                ]
                self.session.add(creator)

    def test_multiple_choice_bucket_choice_from_wrong_question(self):
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                creator, survey = self._create_blank_survey()
                wrong_node = models.construct_node(
                    type_constraint='multiple_choice', title='wrong'
                )
                wrong_choice = models.Choice()
                wrong_node.choices = [wrong_choice]

                survey.nodes = [
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='multiple_choice',
                            title={'English': 'node'},
                            choices=[models.Choice()],
                        ),
                        sub_surveys=[
                            models.SubSurvey(
                                buckets=[
                                    models.construct_bucket(
                                        bucket_type='multiple_choice',
                                        bucket=wrong_choice
                                    ),
                                ],
                            ),
                        ],
                    ),
                ]
                self.session.add(creator)


class TestSubmission(DokoTest):
    def test_administrators(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            admin = models.User(name='admin')
            creator.surveys = [
                models.EnumeratorOnlySurvey(
                    title={'English': 'survey'},
                    administrators=[admin]
                ),
            ]

            self.session.add(creator)

        self.assertIs(
            self.session.query(models.Survey).one().administrators[0],
            self.session.query(models.User).filter_by(name='admin').one()
        )

    def test_enumerator_submission(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            enumerator = models.User(name='enumerator')
            creator.surveys = [
                models.EnumeratorOnlySurvey(
                    title={'English': 'survey'},
                    enumerators=[enumerator]
                ),
            ]

            self.session.add(creator)

            submission = models.EnumeratorOnlySubmission(
                survey=creator.surveys[0],
                enumerator=enumerator,
            )

            self.session.add(submission)

        self.assertIs(
            self.session.query(models.Submission).one().enumerator,
            self.session.query(models.User).filter_by(role='enumerator').one()
        )

    def test_enumerator_only_submission_asdict(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            enumerator = models.User(name='enumerator')
            creator.surveys = [
                models.EnumeratorOnlySurvey(
                    title={'English': 'survey'},
                    enumerators=[enumerator],
                    nodes=[
                        models.construct_survey_node(
                            answerable=True,
                            node=models.construct_node(
                                type_constraint='location',
                                title={'English': 'location?'},
                            ),
                        ),
                    ],
                ),
            ]

            self.session.add(creator)

            submission = models.EnumeratorOnlySubmission(
                survey=creator.surveys[0],
                enumerator=enumerator,
                answers=[
                    models.construct_answer(
                        type_constraint='location',
                        survey_node=creator.surveys[0].nodes[0],
                        answer={'lng': 5, 'lat': 3},
                    ),
                ],
            )

            self.session.add(submission)

        the_submission = self.session.query(models.Submission).one()
        self.assertEqual(
            the_submission._asdict(),
            OrderedDict((
                ('id', the_submission.id),
                ('deleted', False),
                ('survey_id', self.session.query(models.Survey.id).scalar()),
                ('save_time', the_submission.save_time),
                ('submission_time', the_submission.submission_time),
                ('last_update_time', the_submission.last_update_time),
                ('submitter_name', ''),
                ('submitter_email', ''),
                (
                    'answers',
                    [
                        OrderedDict((
                            ('response_type', 'answer'),
                            (
                                'response',
                                '{"type":"Point","coordinates":[5,3]}'
                            ),
                        )),
                    ]
                ),
                (
                    'enumerator_user_id',
                    self.session
                    .query(models.User.id)
                    .filter_by(role='enumerator')
                    .scalar()
                ),
                ('enumerator_user_name', 'enumerator'),
            ))
        )

    def test_enumerator_only(self):
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                creator = models.SurveyCreator(name='creator')
                enumerator = models.User(name='enumerator')
                creator.surveys = [
                    models.EnumeratorOnlySurvey(
                        title={'English': 'survey'},
                    ),
                ]
                creator.enumerators = [enumerator]

                self.session.add(creator)

                submission = models.PublicSubmission(
                    survey=creator.surveys[0],
                )

                self.session.add(submission)

    def test_enumerator_only_submission_requires_enumerator(self):
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                creator = models.SurveyCreator(name='creator')
                enumerator = models.User(name='enumerator')
                creator.surveys = [
                    models.EnumeratorOnlySurvey(
                        title={'English': 'survey'},
                    ),
                ]
                creator.enumerators = [enumerator]

                self.session.add(creator)

                submission = models.EnumeratorOnlySubmission(
                    survey=creator.surveys[0],
                )

                self.session.add(submission)

    def test_non_enumerator_cannot_submit(self):
        with self.assertRaises(IntegrityError):
            with self.session.begin():
                creator = models.SurveyCreator(name='creator')
                creator.surveys = [
                    models.EnumeratorOnlySurvey(
                        title={'English': 'survey'},
                    ),
                ]

                self.session.add(creator)

                bad_user = models.User(name='bad')
                self.session.add(bad_user)

                submission = models.EnumeratorOnlySubmission(
                    survey=creator.surveys[0],
                    enumerator=bad_user,
                )

                self.session.add(submission)

    def test_authentication_not_required_for_regular_survey(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            authentic_user = models.User(name='enumerator')
            creator.surveys = [models.Survey(title={'English': 'survey'})]

            self.session.add(creator)

            auth_submission = models.PublicSubmission(
                survey=creator.surveys[0],
                enumerator=authentic_user,
            )

            self.session.add(auth_submission)

            regular_submission = models.PublicSubmission(
                survey=creator.surveys[0],
                submitter_name='regular',
            )

            self.session.add(regular_submission)

        self.assertEqual(
            self.session.query(func.count(models.Submission.id)).scalar(),
            2
        )
        self.assertEqual(
            self.session
            .query(func.count(models.PublicSubmission.id)).scalar(),
            2
        )
        self.assertEqual(
            self.session
            .query(func.count(models.EnumeratorOnlySubmission.id)).scalar(),
            0
        )

    def test_public_submission_asdict_non_enumerator(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            creator.surveys = [models.Survey(title={'English': 'survey'})]

            self.session.add(creator)

            auth_submission = models.PublicSubmission(
                survey=creator.surveys[0],
                submitter_name='not an enumerator',
                submitter_email='some@email',
            )

            self.session.add(auth_submission)

        the_submission = self.session.query(models.Submission).one()
        self.assertEqual(
            the_submission._asdict(),
            OrderedDict((
                ('id', the_submission.id),
                ('deleted', False),
                ('survey_id', self.session.query(models.Survey.id).scalar()),
                ('save_time', the_submission.save_time),
                ('submission_time', the_submission.submission_time),
                ('last_update_time', the_submission.last_update_time),
                ('submitter_name', 'not an enumerator'),
                ('submitter_email', 'some@email'),
                ('answers', []),
            ))
        )

    def test_public_submission_asdict_enumerator(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            authentic_user = models.User(name='enumerator')
            creator.surveys = [models.Survey(title={'English': 'survey'})]

            self.session.add(creator)

            auth_submission = models.PublicSubmission(
                survey=creator.surveys[0],
                enumerator=authentic_user,
            )

            self.session.add(auth_submission)

        the_submission = self.session.query(models.Submission).one()
        self.assertEqual(
            the_submission._asdict(),
            OrderedDict((
                ('id', the_submission.id),
                ('deleted', False),
                ('survey_id', self.session.query(models.Survey.id).scalar()),
                ('save_time', the_submission.save_time),
                ('submission_time', the_submission.submission_time),
                ('last_update_time', the_submission.last_update_time),
                ('submitter_name', ''),
                ('submitter_email', ''),
                ('answers', []),
                (
                    'enumerator_user_id',
                    self.session
                    .query(models.User.id)
                    .filter_by(role='enumerator')
                    .scalar()
                ),
                ('enumerator_user_name', 'enumerator'),
            ))
        )


class TestAnswer(DokoTest):
    def test_non_instantiable(self):
        self.assertRaises(TypeError, models.Answer)

    def test_basic_case(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'integer question'},
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.session.begin():
            the_survey = self.session.query(models.Survey).one()
            submission = models.PublicSubmission(
                survey=the_survey,
                answers=[
                    models.construct_answer(
                        survey_node=the_survey.nodes[0],
                        type_constraint='integer',
                        answer=3,
                    ),
                ],
            )

            self.session.add(submission)

        self.assertIs(
            self.session.query(models.Answer).one(),
            self.session.query(models.Survey).one().submissions[0].answers[0]
        )
        self.assertEqual(
            self.session.query(models.Answer).one().answer,
            3
        )
        self.assertDictEqual(
            self.session.query(models.Answer).one().response,
            {'response_type': 'answer', 'response': 3}
        )

    def test_asdict(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'integer question'},
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.session.begin():
            the_survey = self.session.query(models.Survey).one()
            submission = models.PublicSubmission(
                survey=the_survey,
                answers=[
                    models.construct_answer(
                        survey_node=the_survey.nodes[0],
                        type_constraint='integer',
                        answer=3,
                    ),
                ],
            )

            self.session.add(submission)

        answer = self.session.query(models.Answer).one()
        self.assertEqual(
            answer._asdict(),
            OrderedDict((
                ('id', answer.id),
                ('deleted', False),
                ('answer_number', 0),
                ('submission_id', answer.submission_id),
                ('submission_time', answer.submission_time),
                ('survey_id', self.session.query(models.Survey.id).scalar()),
                (
                    'survey_node_id',
                    self.session.query(models.SurveyNode.id).scalar()
                ),
                (
                    'question_id',
                    self.session.query(models.Question.id).scalar()
                ),
                ('type_constraint', 'integer'),
                ('last_update_time', answer.last_update_time),
                (
                    'response',
                    OrderedDict((
                        ('response_type', 'answer'), ('response', 3)
                    ))
                ),
            ))
        )

    @test_continues_after_rollback
    def test_cannot_answer_a_note(self):
        with self.session.begin():
            creator = models.SurveyCreator(
                name='creator',
                surveys=[
                    models.Survey(
                        title={'English': 'non_answerable'},
                        nodes=[
                            models.construct_survey_node(
                                answerable=False,
                                node=models.construct_node(
                                    type_constraint='note',
                                    title={'English': "can't answer me!"},
                                ),
                            ),
                        ],
                    ),
                ],
            )
            self.session.add(creator)

        with self.assertRaises(exc.NotAnAnswerTypeError):
            with self.session.begin():
                survey = self.session.query(models.Survey).one()
                submission = models.PublicSubmission(
                    survey=survey,
                    answers=[
                        models.construct_answer(
                            survey_node=survey.nodes[0],
                            type_constraint='note',
                        ),
                    ],
                )
                self.session.add(submission)

        with self.assertRaises(FlushError):
            with self.session.begin():
                survey = self.session.query(models.Survey).one()
                submission = models.PublicSubmission(
                    survey=survey,
                    answers=[
                        models.construct_answer(
                            survey_node=survey.nodes[0],
                            type_constraint='integer',
                            answer=3,
                        ),
                    ],
                )
                self.session.add(submission)

    def test_answer_type_matches_question_type(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'integer question'},
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.assertRaises(IntegrityError):
            with self.session.begin():
                the_survey = self.session.query(models.Survey).one()
                submission = models.PublicSubmission(
                    survey=the_survey,
                    answers=[
                        models.construct_answer(
                            survey_node=the_survey.nodes[0],
                            type_constraint='text',
                            answer='not an integer',
                        ),
                    ],
                )

                self.session.add(submission)

    def test_reject_incorrect_answer_syntax(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'integer question'},
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.assertRaises(DataError):
            with self.session.begin():
                the_survey = self.session.query(models.Survey).one()
                submission = models.PublicSubmission(
                    survey=the_survey,
                    answers=[
                        models.construct_answer(
                            survey_node=the_survey.nodes[0],
                            type_constraint='integer',
                            answer='not an integer',
                        ),
                    ],
                )

                self.session.add(submission)

    def test_text_answer(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='text',
                            title={'English': 'text_question'},
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.session.begin():
            the_survey = self.session.query(models.Survey).one()
            submission = models.PublicSubmission(
                survey=the_survey,
                answers=[
                    models.construct_answer(
                        survey_node=the_survey.nodes[0],
                        type_constraint='text',
                        answer='I can put anything here ಠ_ಠ 你好世界！',
                    ),
                ],
            )

            self.session.add(submission)

        self.assertEqual(
            self.session.query(models.Answer).one().answer,
            'I can put anything here ಠ_ಠ 你好世界！'
        )

    def test_photo_answer(self):
        pass  # TODO...

    def test_integer_answer(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'integer_question'},
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.session.begin():
            the_survey = self.session.query(models.Survey).one()
            submission = models.PublicSubmission(
                survey=the_survey,
                answers=[
                    models.construct_answer(
                        survey_node=the_survey.nodes[0],
                        type_constraint='integer',
                        answer=3,
                    ),
                ],
            )

            self.session.add(submission)

        self.assertEqual(
            self.session.query(models.Answer).one().answer,
            3
        )

    def test_decimal_answer(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='decimal',
                            title={'English': 'decimal_question'},
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.session.begin():
            the_survey = self.session.query(models.Survey).one()
            submission = models.PublicSubmission(
                survey=the_survey,
                answers=[
                    models.construct_answer(
                        survey_node=the_survey.nodes[0],
                        type_constraint='decimal',
                        answer=3.9,
                    ),
                ],
            )

            self.session.add(submission)

        self.assertEqual(
            self.session.query(models.Answer).one().answer,
            Decimal('3.9')
        )

    def test_date_answer(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='date',
                            title={'English': 'date_question'},
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.session.begin():
            the_survey = self.session.query(models.Survey).one()
            submission = models.PublicSubmission(
                survey=the_survey,
                answers=[
                    models.construct_answer(
                        survey_node=the_survey.nodes[0],
                        type_constraint='date',
                        answer='2015/6/22',
                    ),
                ],
            )

            self.session.add(submission)

        self.assertEqual(
            self.session.query(models.Answer).one().answer,
            datetime.date(2015, 6, 22)
        )

    def test_time_answer(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='time',
                            title={'English': 'time_question'},
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.session.begin():
            the_survey = self.session.query(models.Survey).one()
            submission = models.PublicSubmission(
                survey=the_survey,
                answers=[
                    models.construct_answer(
                        survey_node=the_survey.nodes[0],
                        type_constraint='time',
                        answer='1:57 PM',
                    ),
                ],
            )

            self.session.add(submission)

        local_offset = (
            dateutil.tz.tzlocal()
            .utcoffset(datetime.datetime.now())
            .total_seconds() / 60
        )
        self.assertEqual(
            self.session.query(models.Answer).one().answer,
            datetime.time(
                13, 57,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=local_offset)
            )
        )

    def test_timestamp_answer(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='timestamp',
                            title={'English': 'timestamp_question'},
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.session.begin():
            the_survey = self.session.query(models.Survey).one()
            submission = models.PublicSubmission(
                survey=the_survey,
                answers=[
                    models.construct_answer(
                        survey_node=the_survey.nodes[0],
                        type_constraint='timestamp',
                        answer='2015/06/22 1:57 PM',
                    ),
                ],
            )

            self.session.add(submission)

        local_offset = (
            dateutil.tz.tzlocal()
            .utcoffset(datetime.datetime.now())
            .total_seconds() / 60
        )
        self.assertEqual(
            self.session.query(models.Answer).one().answer,
            datetime.datetime(
                2015, 6, 22, 13, 57,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=local_offset)
            )
        )

    def test_location_answer(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='location',
                            title={'English': 'location_question'},
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.session.begin():
            the_survey = self.session.query(models.Survey).one()
            submission = models.PublicSubmission(
                survey=the_survey,
                answers=[
                    models.construct_answer(
                        survey_node=the_survey.nodes[0],
                        type_constraint='location',
                        answer={'lng': 5, 'lat': -5},
                    ),
                ],
            )

            self.session.add(submission)

        self.assertEqual(
            json.loads(self.session.query(models.Answer).one().answer),
            {'type': 'Point', 'coordinates': [5, -5]}
        )

    def test_facility_answer(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='facility',
                            title={'English': 'facility_question'},
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.session.begin():
            the_survey = self.session.query(models.Survey).one()
            submission = models.PublicSubmission(
                survey=the_survey,
                answers=[
                    models.construct_answer(
                        survey_node=the_survey.nodes[0],
                        type_constraint='facility',
                        answer={
                            'facility_location': {'lng': 5, 'lat': -5},
                            'facility_id': '1',
                            'facility_name': 'SEL',
                            'facility_sector': 'engineering',
                        },
                    ),
                ],
            )

            self.session.add(submission)

        answer = self.session.query(models.Answer).one().answer
        self.assertEqual(
            json.loads(answer['facility_location']),
            {'type': 'Point', 'coordinates': [5, -5]}
        )
        self.assertEqual(answer['facility_id'], '1')
        self.assertEqual(answer['facility_name'], 'SEL')
        self.assertEqual(answer['facility_sector'], 'engineering')

    def test_multiple_choice_answer(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='multiple_choice',
                            title={'English': 'multiple_choice_question'},
                            choices=[models.Choice(choice_text={
                                'English': 'one'
                            })],
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.session.begin():
            the_survey = self.session.query(models.Survey).one()
            submission = models.PublicSubmission(
                survey=the_survey,
                answers=[
                    models.construct_answer(
                        survey_node=the_survey.nodes[0],
                        type_constraint='multiple_choice',
                        answer=the_survey.nodes[0].node.choices[0],
                    ),
                ],
            )

            self.session.add(submission)

        self.assertEqual(
            self.session.query(models.Answer).one().answer.choice_text,
            {'English': 'one'}
        )

    def test_answer_choice_belongs_to_question(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={"English": "survey"},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='multiple_choice',
                            title={"English": "multiple_choice_question_1"},
                            choices=[models.Choice(
                                choice_text={'English': 'only one'}
                            )],
                        ),
                    ),
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='multiple_choice',
                            title={"English": "multiple_choice_question_2"},
                            choices=[models.Choice(
                                choice_text={'English': 'only one'}
                            )],
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.assertRaises(IntegrityError):
            with self.session.begin():
                the_survey = self.session.query(models.Survey).one()
                submission = models.PublicSubmission(
                    survey=the_survey,
                    answers=[
                        models.construct_answer(
                            survey_node=the_survey.nodes[0],
                            type_constraint='multiple_choice',
                            answer=the_survey.nodes[1].node.choices[0],
                        ),
                    ],
                )

                self.session.add(submission)

    def test_cant_answer_other_by_default(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'other_not_allowed'},
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.assertRaises(IntegrityError):
            with self.session.begin():
                the_survey = self.session.query(models.Survey).one()
                submission = models.PublicSubmission(
                    survey=the_survey,
                    answers=[
                        models.construct_answer(
                            survey_node=the_survey.nodes[0],
                            type_constraint='integer',
                            other='other',
                        ),
                    ],
                )

                self.session.add(submission)

    def test_only_MC_can_allow_other(self):
        if True:
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'integer bad'},
                            allow_other=True,
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

    def test_answer_other(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='multiple_choice',
                            title={'English': 'other_not_allowed'},
                            allow_other=True,
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.session.begin():
            the_survey = self.session.query(models.Survey).one()
            submission = models.PublicSubmission(
                survey=the_survey,
                answers=[
                    models.construct_answer(
                        survey_node=the_survey.nodes[0],
                        type_constraint='multiple_choice',
                        other='other answer',
                    ),
                ],
            )

            self.session.add(submission)

        self.assertEqual(
            self.session.query(models.Answer).one().other,
            'other answer'
        )
        self.assertDictEqual(
            self.session.query(models.Answer).one().response,
            {'response_type': 'other', 'response': 'other answer'}
        )

    def test_cant_give_answer_and_other(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='multiple_choice',
                            title={'English': 'other allowed'},
                            allow_other=True,
                            choices=[
                                models.Choice(
                                    choice_text={'English': 'choice'},
                                ),
                            ],
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.assertRaises(IntegrityError):
            with self.session.begin():
                the_survey = self.session.query(models.Survey).one()
                submission = models.PublicSubmission(
                    survey=the_survey,
                    answers=[
                        models.construct_answer(
                            survey_node=the_survey.nodes[0],
                            type_constraint='multiple_choice',
                            answer=self.session.query(models.Choice).one(),
                            other='other answer',
                        ),
                    ],
                )

                self.session.add(submission)

    def test_cant_answer_dont_know_by_default(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'dont_know_not_allowed'},
                        ),
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.assertRaises(IntegrityError):
            with self.session.begin():
                the_survey = self.session.query(models.Survey).one()
                submission = models.PublicSubmission(
                    survey=the_survey,
                    answers=[
                        models.construct_answer(
                            survey_node=the_survey.nodes[0],
                            type_constraint='integer',
                            dont_know='dont_know',
                        ),
                    ],
                )

                self.session.add(submission)

    def test_answer_dont_know(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'dont_know_not_allowed'},
                        ),
                        allow_dont_know=True,
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.session.begin():
            the_survey = self.session.query(models.Survey).one()
            submission = models.PublicSubmission(
                survey=the_survey,
                answers=[
                    models.construct_answer(
                        survey_node=the_survey.nodes[0],
                        type_constraint='integer',
                        dont_know='dont_know answer',
                    ),
                ],
            )

            self.session.add(submission)

        self.assertEqual(
            self.session.query(models.Answer).one().dont_know,
            'dont_know answer'
        )
        self.assertDictEqual(
            self.session.query(models.Answer).one().response,
            {'response_type': 'dont_know', 'response': 'dont_know answer'}
        )

    def test_cant_give_answer_and_dont_know(self):
        with self.session.begin():
            creator = models.SurveyCreator(name='creator')
            survey = models.Survey(
                title={'English': 'survey'},
                nodes=[
                    models.construct_survey_node(
                        answerable=True,
                        node=models.construct_node(
                            type_constraint='integer',
                            title={'English': 'dont_know allowed'},
                        ),
                        allow_dont_know=True,
                    ),
                ],
            )
            creator.surveys = [survey]

            self.session.add(creator)

        with self.assertRaises(IntegrityError):
            with self.session.begin():
                the_survey = self.session.query(models.Survey).one()
                submission = models.PublicSubmission(
                    survey=the_survey,
                    answers=[
                        models.construct_answer(
                            survey_node=the_survey.nodes[0],
                            type_constraint='integer',
                            answer=3,
                            dont_know='dont_know answer',
                        ),
                    ],
                )

                self.session.add(submission)
