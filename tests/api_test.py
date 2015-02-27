"""
Tests for the dokomo JSON api

"""
import unittest
import uuid
from sqlalchemy import and_
from datetime import datetime, timedelta, date
from math import sqrt

from sqlalchemy.exc import ProgrammingError
from sqlalchemy.exc import DataError, IntegrityError
from passlib.hash import bcrypt_sha256

from api import execute_with_exceptions
import api.survey
import api.submission
import api.user
import api.aggregation
import db
from db.answer import answer_insert, CannotAnswerMultipleTimesError, \
    get_answers
from db.answer_choice import get_answer_choices
from db.auth_user import auth_user_table, create_auth_user, get_auth_user, \
    get_auth_user_by_email
from db.question import question_table, get_questions_no_credentials, \
    QuestionDoesNotExistError, MissingMinimalLogicError
from db.question_branch import get_branches, MultipleBranchError
from db.question_choice import question_choice_table, get_choices, \
    RepeatedChoiceError, QuestionChoiceDoesNotExistError
from db.submission import submission_table, submission_insert, \
    SubmissionDoesNotExistError, submission_select, get_submissions_by_email
from db.survey import survey_table, survey_select, SurveyDoesNotExistError
from db.type_constraint import TypeConstraintDoesNotExistError


connection = db.engine.connect()


class TestSubmission(unittest.TestCase):
    def tearDown(self):
        connection.execute(submission_table.delete())
        condition = survey_table.c.survey_title.in_(
            ('survey with required question',))
        connection.execute(survey_table.delete().where(condition))

    def testSubmit(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        question_id = connection.execute(question_table.select().where(
            and_cond)).first().question_id
        second_cond = and_(question_table.c.survey_id == survey_id,
                           question_table.c.type_constraint_name ==
                           'multiple_choice')
        second_q_id = connection.execute(question_table.select().where(
            second_cond)).first().question_id
        choice_cond = question_choice_table.c.question_id == second_q_id
        choice_id = connection.execute(question_choice_table.select().where(
            choice_cond)).first().question_choice_id
        third_cond = and_(question_table.c.survey_id == survey_id,
                          question_table.c.type_constraint_name == 'text')
        third_q_id = connection.execute(question_table.select().where(
            third_cond)).first().question_id
        fourth_cond = and_(question_table.c.survey_id == survey_id,
                           question_table.c.type_constraint_name == 'decimal')
        fourth_q_id = connection.execute(question_table.select().where(
            fourth_cond)).first().question_id
        input_data = {'submitter': 'me',
                      'survey_id': survey_id,
                      'answers':
                          [{'question_id': question_id,
                            'answer': 1,
                            'is_other': False},
                           {'question_id': second_q_id,
                            'answer': choice_id,
                            'is_other': False},
                           {'question_id': third_q_id,
                            'answer': 'answer one',
                            'is_other': False},
                           {'question_id': third_q_id,
                            'answer': 'answer two',
                            'is_other': False},
                           {'question_id': fourth_q_id,
                            'answer': 3.5,
                            'is_other': False}]}
        response = api.submission.submit(connection, input_data)['result']
        submission_id = response['submission_id']
        condition = submission_table.c.submission_id == submission_id
        self.assertEqual(connection.execute(
            submission_table.select().where(condition)).rowcount, 1)
        data = api.submission.get_one(connection, submission_id,
                                      email='test_email')['result']
        self.assertEqual(response, data)
        self.assertEqual(data['answers'][0]['answer'], 1)
        self.assertEqual(data['answers'][1]['answer'], choice_id)
        self.assertEqual(data['answers'][2]['answer'], 3.5)
        self.assertEqual(data['answers'][3]['answer'], 'answer one')
        self.assertEqual(data['answers'][4]['answer'], 'answer two')

    def testIncorrectType(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        question_id = connection.execute(question_table.select().where(
            and_cond)).first().question_id
        input_data = {'submitter': 'me',
                      'survey_id': survey_id,
                      'answers':
                          [{'question_id': question_id,
                            'answer': 'one',
                            'is_other': False}]}
        self.assertRaises(DataError, api.submission.submit, connection,
                          input_data)
        self.assertEqual(
            connection.execute(submission_table.select()).rowcount, 0)

        input_data2 = {'survey_id': survey_id,
                       'submitter': 'test_submitter',
                       'answers':
                           [{'question_id': question_id,
                             'answer': 1j,
                             'is_other': False}]}
        self.assertRaises(ProgrammingError, api.submission.submit, connection,
                          input_data2)

    def testIsOther(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        question_id = connection.execute(question_table.select().where(
            and_cond)).first().question_id
        input_data = {'survey_id': survey_id,
                      'submitter': 'test_submitter',
                      'answers':
                          [{'question_id': question_id,
                            'answer': 'one',
                            'is_other': True}]}
        result = api.submission.submit(connection, input_data)['result']
        self.assertEqual(result['answers'][0]['answer'], 'one')
        self.assertEqual(result['answers'][0]['is_other'], True)

    def testSkippedQuestion(self):
        questions = [{'question_title': 'required question',
                      'type_constraint_name': 'integer',
                      'sequence_number': None,
                      'question_to_sequence_number': -1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': True, 'with_other': False},
                      'choices': None,
                      'branches': None}]
        data = {'survey_title': 'survey with required question',
                'questions': questions,
                'email': 'test_email'}
        survey = api.survey.create(connection, data)['result']
        survey_id = survey['survey_id']

        submission = {'submitter': 'me',
                      'survey_id': survey_id,
                      'answers': []}
        self.assertRaises(api.submission.RequiredQuestionSkippedError,
                          api.submission.submit, connection, submission)

        question_id = survey['questions'][0]['question_id']

        submission2 = {'submitter': 'me',
                       'survey_id': survey_id,
                       'answers': [{'question_id': question_id,
                                    'answer': None}]}

        self.assertRaises(api.submission.RequiredQuestionSkippedError,
                          api.submission.submit, connection, submission2)

    def testQuestionDoesNotExist(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first(

        ).survey_id
        input_data = {'submitter': 'me',
                      'survey_id': survey_id,
                      'answers': [{'question_id': str(uuid.uuid4()),
                                   'answer': 1}]}
        self.assertRaises(QuestionDoesNotExistError,
                          api.submission.submit,
                          connection,
                          input_data)

    def testSurveyDoesNotExist(self):
        survey_id = str(uuid.uuid4())
        input_data = {'submitter': 'me', 'survey_id': survey_id, 'answers': []}
        self.assertRaises(SurveyDoesNotExistError, api.submission.submit,
                          connection,
                          input_data)

    def testDateAndTime(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        date_cond = and_(question_table.c.survey_id == survey_id,
                         question_table.c.type_constraint_name == 'date')
        date_question_id = connection.execute(question_table.select().where(
            date_cond)).first().question_id
        time_cond = and_(question_table.c.survey_id == survey_id,
                         question_table.c.type_constraint_name == 'time')
        time_question_id = connection.execute(question_table.select().where(
            time_cond)).first().question_id
        input_data = {'submitter': 'me',
                      'survey_id': survey_id,
                      'answers':
                          [{'question_id': date_question_id,
                            'answer': '2014-10-27',
                            'is_other': False},
                           {'question_id': time_question_id,
                            'answer': '11:26-04:00',
                            'is_other': False}]}  # UTC-04:00
        response = api.submission.submit(connection, input_data)['result']
        self.assertEqual(response['answers'][0]['answer'], '2014-10-27')
        self.assertEqual(response['answers'][1]['answer'], '11:26:00-04:00')

    def testMultipleAnswersNotAllowed(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        question_id = connection.execute(question_table.select().where(
            and_cond)).first().question_id
        input_data = {'submitter': 'me',
                      'survey_id': survey_id,
                      'answers':
                          [{'question_id': question_id,
                            'answer': 1,
                            'is_other': False},
                           {'question_id': question_id,
                            'answer': 2,
                            'is_other': False}]}
        self.assertRaises(CannotAnswerMultipleTimesError,
                          api.submission.submit,
                          connection,
                          input_data)

    def testGet(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'location')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = connection.execute(
            submission_insert(submitter='test_submitter',
                              survey_id=survey_id))
        submission_id = submission_exec.inserted_primary_key[0]
        connection.execute(answer_insert(
            answer=[90, 0], question_id=question_id,
            submission_id=submission_id, survey_id=survey_id,
            type_constraint_name=tcn, is_other=False, sequence_number=seq,
            allow_multiple=mul))
        data = api.submission.get_one(connection, submission_id,
                                      email='test_email')['result']
        self.assertIsNotNone(data['submission_id'])
        self.assertIsNotNone(data['answers'])

    def testGetForSurvey(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        for i in range(2):
            submission_exec = connection.execute(
                submission_insert(submitter='test_submitter',
                                  survey_id=survey_id))
            submission_id = submission_exec.inserted_primary_key[0]
            connection.execute(answer_insert(
                answer=i, question_id=question_id, submission_id=submission_id,
                survey_id=survey_id, type_constraint_name=tcn, is_other=False,
                sequence_number=seq, allow_multiple=mul))
        data = api.submission.get_all(connection, survey_id,
                                      email='test_email')
        self.assertGreater(len(data), 0)

    def testDelete(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        data = {'submitter': 'me',
                'survey_id': survey_id,
                'answers': [{'answer': None}]}
        submission_id = api.submission.submit(connection, data)['result'][
            'submission_id']
        api.submission.delete(connection, submission_id)
        self.assertRaises(SubmissionDoesNotExistError,
                          submission_select,
                          connection,
                          submission_id,
                          email='test_email')


class TestSurvey(unittest.TestCase):
    def tearDown(self):
        condition = survey_table.c.survey_title.in_(('updated',))
        connection.execute(survey_table.delete().where(condition))
        connection.execute(survey_table.delete().where(
            survey_table.c.survey_title.like('to_be_updated%')))
        connection.execute(survey_table.delete().where(
            survey_table.c.survey_title.like('bad update survey%')))
        connection.execute(survey_table.delete().where(
            survey_table.c.survey_title.like('api_test survey%')))
        connection.execute(survey_table.delete().where(
            survey_table.c.survey_title.like('test_title(%')))
        connection.execute(survey_table.delete().where(
            survey_table.c.survey_title.like(
                'updated survey title%')))
        connection.execute(survey_table.delete().where(
            survey_table.c.survey_title.like('not in conflict%')))
        connection.execute(submission_table.delete())

    def testGetOne(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        data = api.survey.get_one(connection, survey_id, email='test_email')[
            'result']
        self.assertIsNotNone(data['survey_id'])
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['metadata'])

    def testDisplaySurvey(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        data = api.survey.display_survey(connection, survey_id)['result']
        self.assertIsNotNone(data['survey_id'])
        self.assertIsNotNone(data['questions'])

    def testGetAll(self):
        email = connection.execute(auth_user_table.select().where(
            auth_user_table.c.email == 'test_email')).first().email
        surveys = api.survey.get_all(connection, email)['result']
        self.assertGreater(len(surveys), 0)

    def testCreate(self):
        questions = [{'question_title': 'api_test mc question',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': ['choice 1', 'choice 2'],
                      'branches': [{'choice_number': 0,
                                    'to_question_number': 2}]},
                     {'question_title': 'api_test question',
                      'type_constraint_name': 'text',
                      'sequence_number': None,
                      'question_to_sequence_number': -1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False,
                                'with_other': False,
                                'min': 3},
                      'choices': None,
                      'branches': None}]
        data = {'survey_title': 'api_test survey',
                'questions': questions,
                'email': 'test_email'}
        survey_id = api.survey.create(connection, data)['result']['survey_id']
        condition = survey_table.c.survey_id == survey_id
        self.assertEqual(connection.execute(
            survey_table.select().where(condition)).rowcount, 1)
        questions = list(get_questions_no_credentials(connection, survey_id))
        self.assertEqual(questions[1].logic,
                         {'required': False, 'with_other': False, 'min': 3})
        self.assertEqual(
            get_choices(connection, questions[0].question_id).first().choice,
            'choice 1')

    def testLogicMissing(self):
        questions = [{'question_title': 'api_test mc question',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': -1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {},
                      'choices': ['choice 1', 'choice 2'],
                      'branches': [{'choice_number': 0,
                                    'to_question_number': 1}]}]
        data = {'survey_title': 'api_test survey',
                'questions': questions,
                'email': 'test_email'}
        self.assertRaises(MissingMinimalLogicError, api.survey.create,
                          connection, data)

    def testSurveyDoesNotEnd(self):
        questions = [{'question_title': 'api_test mc question',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False,
                                'with_other': False},
                      'choices': None,
                      'branches': None}]
        data = {'survey_title': 'api_test survey',
                'questions': questions,
                'email': 'test_email'}

        self.assertRaises(api.survey.SurveyDoesNotEndError,
                          api.survey.create, connection, data)

    def testSurveyAlreadyExists(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        title = survey_select(connection, survey_id,
                              email='test_email').survey_title
        input_data = {'survey_title': title,
                      'questions': [{'question_title': 'none',
                                     'type_constraint_name': 'text',
                                     'question_to_sequence_number': -1,
                                     'hint': None,
                                     'allow_multiple': False,
                                     'logic': {'required': False,
                                               'with_other': False},
                                     'choices': None,
                                     'branches': None}],
                      'email': 'test_email'}
        result = api.survey.create(connection, input_data)['result']
        self.assertEqual(result['survey_title'], 'test_title(1)')
        result2 = api.survey.create(connection, input_data)['result']
        self.assertEqual(result2['survey_title'], 'test_title(2)')
        result3 = api.survey.create(connection,
                                    {'survey_title': 'test_title(1)',
                                     'questions': [
                                         {'question_title': 'none',
                                          'type_constraint_name': 'text',
                                          'question_to_sequence_number': -1,
                                          'hint': None,
                                          'allow_multiple': False,
                                          'logic': {'required': False,
                                                    'with_other': False},
                                          'choices': None,
                                          'branches': None}
                                     ],
                                     'email': 'test_email'})['result']
        self.assertEqual(result3['survey_title'], 'test_title(1)(1)')

        dummy_questions = [{'question_title': 'none',
                            'type_constraint_name': 'text',
                            'question_to_sequence_number': -1,
                            'hint': None,
                            'allow_multiple': False,
                            'logic': {'required': False,
                                      'with_other': False},
                            'choices': None,
                            'branches': None}]

        api.survey.create(connection, {'survey_title': 'not in conflict(1)',
                                       'questions': dummy_questions,
                                       'email': 'test_email'})
        result4 = \
            api.survey.create(connection, {'survey_title': 'not in conflict',
                                           'questions': dummy_questions,
                                           'email': 'test_email'})['result']
        self.assertEqual(result4['survey_title'], 'not in conflict')

    def testTwoChoicesWithSameName(self):
        input_data = {'survey_title': 'choice error',
                      'email': 'test_email',
                      'questions': [{'question_title': 'choice error',
                                     'type_constraint_name': 'multiple_choice',
                                     'sequence_number': None,
                                     'question_to_sequence_number': 1,
                                     'hint': None,
                                     'allow_multiple': False,
                                     'logic': {'required': False,
                                               'with_other': False},
                                     'choices': ['a', 'a']}]}
        self.assertRaises(RepeatedChoiceError, api.survey.create, connection,
                          input_data)

    def testTwoBranchesFromOneChoice(self):
        input_data = {'survey_title': 'choice error',
                      'email': 'test_email',
                      'questions': [{'question_title': 'choice error',
                                     'type_constraint_name': 'multiple_choice',
                                     'sequence_number': None,
                                     'question_to_sequence_number': 1,
                                     'hint': None,
                                     'allow_multiple': False,
                                     'logic': {'required': False,
                                               'with_other': False},
                                     'choices': ['a', 'b'],
                                     'branches': [{'choice_number': 0,
                                                   'to_question_number': 2},
                                                  {'choice_number': 0,
                                                   'to_question_number': 3}]},
                                    {'question_title': 'choice error',
                                     'type_constraint_name': 'text',
                                     'sequence_number': None,
                                     'question_to_sequence_number': 1,
                                     'hint': None,
                                     'allow_multiple': False,
                                     'logic': {'required': False,
                                               'with_other': False},
                                     'choices': None,
                                     'branches': None},
                                    {'question_title': 'choice error',
                                     'type_constraint_name': 'text',
                                     'sequence_number': None,
                                     'question_to_sequence_number': -1,
                                     'hint': None,
                                     'allow_multiple': False,
                                     'logic': {'required': False,
                                               'with_other': False},
                                     'choices': None,
                                     'branches': None}]}
        self.assertRaises(MultipleBranchError, api.survey.create, connection,
                          input_data)

    def testTypeConstraintDoesNotExist(self):
        input_data = {'survey_title': 'type constraint error',
                      'email': 'test_email',
                      'questions': [{'question_title': 'type constraint error',
                                     'type_constraint_name': 'not real',
                                     'sequence_number': None,
                                     'question_to_sequence_number': 1,
                                     'hint': None,
                                     'allow_multiple': False,
                                     'logic': {'required': False,
                                               'with_other': False}}]}
        self.assertRaises(TypeConstraintDoesNotExistError, api.survey.create,
                          connection,
                          input_data)
        condition = survey_table.c.survey_title == 'type constraint error'
        self.assertEqual(connection.execute(
            survey_table.select().where(condition)).rowcount, 0)

    def testUpdate(self):
        questions = [{'question_title': 'api_test question',
                      'type_constraint_name': 'integer',
                      'sequence_number': None,
                      'question_to_sequence_number': 1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': [],
                      'branches': []},
                     {'question_title': 'api_test 2nd question',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': ['1', '2', '3'],
                      'branches': [
                          {'choice_number': 0, 'to_question_number': 3}]},
                     {'question_title': 'api_test 3rd question',
                      'type_constraint_name': 'text',
                      'sequence_number': None,
                      'question_to_sequence_number': -1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': [],
                      'branches': []}]
        data = {'survey_title': 'api_test survey',
                'questions': questions,
                'email': 'test_email'}
        survey_id = api.survey.create(connection, data)['result']['survey_id']
        inserted_qs = get_questions_no_credentials(connection,
                                                   survey_id).fetchall()
        choice_1 = get_choices(
            connection, inserted_qs[1].question_id).fetchall()[0]
        choice_1_id = choice_1.question_choice_id

        submission = {'submitter': 'me',
                      'survey_id': survey_id,
                      'answers': [{'question_id': inserted_qs[0].question_id,
                                   'answer': 5,
                                   'is_other': False},
                                  {'question_id': inserted_qs[1].question_id,
                                   'answer': choice_1_id,
                                   'is_other': False}]}
        api.submission.submit(connection, submission)

        update_json = {'survey_id': survey_id,
                       'survey_title': 'updated survey title',
                       'email': 'test_email'}
        questions = [{'question_id': inserted_qs[1].question_id,
                      'question_title': 'api_test 2nd question',
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': 1,
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False,
                                'with_other': False,
                                'max': 'one'},
                      'choices': [{'old_choice': '2', 'new_choice': 'b'},
                                  'a',
                                  '1'],
                      'branches': [
                          {'choice_number': 1, 'to_question_number': 3}]},
                     {'question_id': inserted_qs[0].question_id,
                      'question_title': 'updated question title',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'type_constraint_name': 'integer',
                      'question_to_sequence_number': 1,
                      'choices': [],
                      'branches': []},
                     {'question_title': 'second question',
                      'type_constraint_name': 'integer',
                      'sequence_number': None,
                      'question_to_sequence_number': -1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': [],
                      'branches': []}]
        update_json['questions'] = questions
        new_survey = api.survey.update(connection, update_json)
        new_survey_id = new_survey['result']['survey_id']
        upd_survey = survey_select(connection, new_survey_id,
                                   email='test_email')
        upd_questions = get_questions_no_credentials(connection,
                                                     new_survey_id).fetchall()
        branch = get_branches(connection, upd_questions[0].question_id).first()
        self.assertEqual(branch.to_question_id, upd_questions[2].question_id)
        self.assertEqual(upd_questions[0].question_title,
                         'api_test 2nd question')
        self.assertEqual(upd_questions[0].logic,
                         {'required': False,
                          'with_other': False,
                          'max': 'one'})
        self.assertEqual(upd_survey.survey_title, 'updated survey title')
        self.assertEqual(upd_questions[1].question_title,
                         'updated question title')
        choices = get_choices(connection,
                              upd_questions[0].question_id).fetchall()
        self.assertEqual(choices[0].choice, 'b')
        self.assertEqual(choices[1].choice, 'a')
        self.assertEqual(choices[2].choice, '1')
        self.assertEqual(len(choices), 3)
        new_submission = get_submissions_by_email(connection, new_survey_id,
                                                  email='test_email').first()
        integer_answer = get_answers(connection,
                                     new_submission.submission_id).first()
        self.assertEqual(integer_answer.answer_integer, 5)
        the_choice = get_answer_choices(connection,
                                        new_submission.submission_id).first()
        self.assertEqual(the_choice.question_choice_id,
                         choices[2].question_choice_id)

    def testUpdateTypeConstraintChange(self):
        questions = [{'question_title': 'was text question',
                      'type_constraint_name': 'text',
                      'sequence_number': None,
                      'question_to_sequence_number': 2,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': [],
                      'branches': []},
                     {'question_title': 'was multiple choice',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 3,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': ['1', '2', '3'],
                      'branches': []},
                     {'question_title': 'was multiple choice 2',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 4,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': ['a', 'b', 'c'],
                      'branches': []},
                     {'question_title': 'was with other',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 5,
                      'hint': None,
                      'allow_multiple': True,
                      'logic': {'required': False, 'with_other': True},
                      'choices': ['use other'],
                      'branches': []},
                     {'question_title': 'was with other 2',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 6,
                      'hint': None,
                      'allow_multiple': True,
                      'logic': {'required': False, 'with_other': True},
                      'choices': ['use other 2'],
                      'branches': []},
                     {'question_title': 'was with other, lose choices',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': -1,
                      'hint': None,
                      'allow_multiple': True,
                      'logic': {'required': False, 'with_other': True},
                      'choices': ['use other 3'],
                      'branches': []}]
        data = {'survey_title': 'to_be_updated',
                'questions': questions,
                'email': 'test_email'}
        survey_id = api.survey.create(connection, data)['result']['survey_id']
        inserted_qs = get_questions_no_credentials(connection,
                                                   survey_id).fetchall()
        choice_1 = get_choices(connection, inserted_qs[1].question_id).first()
        choice_1_id = choice_1.question_choice_id
        choice_a = get_choices(connection, inserted_qs[2].question_id).first()
        choice_a_id = choice_a.question_choice_id
        other_choice = get_choices(connection,
                                   inserted_qs[3].question_id).first()
        other_choice_id = other_choice.question_choice_id
        other_choice_2 = get_choices(connection,
                                     inserted_qs[4].question_id).first()
        other_choice_2_id = other_choice_2.question_choice_id

        submission = {'submitter': 'me',
                      'survey_id': survey_id,
                      'answers': [{'question_id': inserted_qs[0].question_id,
                                   'answer': 'text answer',
                                   'is_other': False},
                                  {'question_id': inserted_qs[1].question_id,
                                   'answer': choice_1_id,
                                   'is_other': False},
                                  {'question_id': inserted_qs[2].question_id,
                                   'answer': choice_a_id,
                                   'is_other': False},
                                  {'question_id': inserted_qs[3].question_id,
                                   'answer': 'my fancy other answer',
                                   'is_other': True},
                                  {'question_id': inserted_qs[3].question_id,
                                   'answer': other_choice_id,
                                   'is_other': False},
                                  {'question_id': inserted_qs[4].question_id,
                                   'answer': 'my fancier other answer',
                                   'is_other': True},
                                  {'question_id': inserted_qs[4].question_id,
                                   'answer': other_choice_2_id,
                                   'is_other': False},
                                  {'question_id': inserted_qs[5].question_id,
                                   'answer': 'my super fancy other answer',
                                   'is_other': True}]}

        api.submission.submit(connection, submission)

        update_json = {'survey_id': survey_id,
                       'survey_title': 'updated',
                       'email': 'test_email'}
        questions = [{'question_id': inserted_qs[0].question_id,
                      'question_title': 'was text question, '
                                        'now multiple_choice',
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': 1,
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'choices': [],
                      'branches': []},
                     {'question_id': inserted_qs[1].question_id,
                      'question_title': 'was multiple choice, now location',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'type_constraint_name': 'location',
                      'question_to_sequence_number': 1,
                      'choices': [],
                      'branches': []},
                     {'question_id': inserted_qs[2].question_id,
                      'question_title': 'was multiple choice, now with other',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': True},
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': 1,
                      'choices': ['a'],
                      'branches': []},
                     {'question_id': inserted_qs[3].question_id,
                      'question_title': 'lost with other',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': 1,
                      'choices': ['use other'],
                      'branches': []},
                     {'question_id': inserted_qs[4].question_id,
                      'question_title': 'lost with other 2',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'type_constraint_name': 'text',
                      'question_to_sequence_number': 1,
                      'choices': [],
                      'branches': []},
                     {'question_id': inserted_qs[4].question_id,
                      'question_title': 'lost choices',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': True},
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': -1,
                      'choices': [],
                      'branches': []}]
        update_json['questions'] = questions
        new_survey = api.survey.update(connection, update_json)['result']
        gsb = get_submissions_by_email
        new_submissions = gsb(connection, new_survey['survey_id'],
                              email='test_email').fetchall()
        self.assertEqual(len(new_submissions), 1)
        choices = get_answer_choices(connection,
                                     new_submissions[
                                         0].submission_id).fetchall()
        self.assertEqual(len(choices), 2)
        answers = get_answers(connection,
                              new_submissions[0].submission_id).fetchall()
        self.assertEqual(len(answers), 1)

    def testLyingAboutOther(self):
        questions = [{'question_title': 'really with other',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': -1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': True},
                      'choices': ['use other'],
                      'branches': []}]
        data = {'survey_title': 'to_be_updated',
                'questions': questions,
                'email': 'test_email'}

        survey_id = api.survey.create(connection, data)['result']['survey_id']
        inserted_q_id = get_questions_no_credentials(connection,
                                                     survey_id).first(

        ).question_id

        submission = {'submitter': 'me',
                      'survey_id': survey_id,
                      'answers': [{'question_id': inserted_q_id,
                                   'answer': 'text answer',
                                   'is_other': False}]}

        self.assertRaises(DataError, api.submission.submit, connection,
                          submission)

    def testUpdateBadChoices(self):
        questions = [{'question_title': 'bad update question',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': -1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': ['one', 'two'],
                      'branches': []}]
        data = {'survey_title': 'bad update survey',
                'questions': questions,
                'email': 'test_email'}
        survey_id = api.survey.create(connection, data)['result']['survey_id']
        inserted_questions = get_questions_no_credentials(connection,
                                                          survey_id).fetchall()

        update_json = {'survey_id': survey_id,
                       'survey_title': 'updated survey title',
                       'email': 'test_email'}
        questions = [{'question_id': inserted_questions[0].question_id,
                      'question_title': 'updated question title',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': 1,
                      'choices': ['two', 'one', 'one'],
                      'branches': []}]
        update_json['questions'] = questions
        self.assertRaises(RepeatedChoiceError, api.survey.update, connection,
                          update_json)

        questions = [{'question_id': inserted_questions[0].question_id,
                      'question_title': 'updated question title',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': 1,
                      'choices': [
                          {'old_choice': 'three', 'new_choice': 'four'}],
                      'branches': []}]

        update_json['questions'] = questions
        self.assertRaises(QuestionChoiceDoesNotExistError, api.survey.update,
                          connection, update_json)

        questions = [{'question_id': inserted_questions[0].question_id,
                      'question_title': 'updated question title',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': -1,
                      'choices': [
                          {'old_choice': 'one', 'new_choice': 'two'}, 'two'],
                      'branches': []}]

        update_json['questions'] = questions
        self.assertRaises(RepeatedChoiceError, api.survey.update, connection,
                          update_json)

        questions = [{'question_id': inserted_questions[0].question_id,
                      'question_title': 'updated question title',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': -1,
                      'choices': [
                          {'old_choice': 'one', 'new_choice': 'two'},
                          {'old_choice': 'one', 'new_choice': 'three'}],
                      'branches': []}]

        update_json['questions'] = questions
        self.assertRaises(RepeatedChoiceError, api.survey.update, connection,
                          update_json)

    def testDelete(self):
        data = {'survey_title': 'api_test survey',
                'questions': [{'question_title': 'none',
                               'type_constraint_name': 'text',
                               'question_to_sequence_number': -1,
                               'hint': None,
                               'allow_multiple': False,
                               'logic': {'required': False,
                                         'with_other': False},
                               'choices': None,
                               'branches': None}],
                'email': 'test_email'}
        survey_id = api.survey.create(connection, data)['result']['survey_id']
        api.survey.delete(connection, survey_id)
        self.assertRaises(SurveyDoesNotExistError, survey_select, connection,
                          survey_id,
                          email='test_email')


class TestUtils(unittest.TestCase):
    def testExecuteWithExceptions(self):
        executable = survey_table.insert({'survey_title': ''})
        with db.engine.begin() as connection:
            self.assertRaises(ValueError, execute_with_exceptions, connection,
                              executable, [('null value', ValueError)])
        with db.engine.begin() as connection:
            self.assertRaises(IntegrityError, execute_with_exceptions,
                              connection, executable,
                              [('not in the error', ValueError)])


class TestAPIToken(unittest.TestCase):
    def tearDown(self):
        connection.execute(auth_user_table.delete().where(
            auth_user_table.c.email == 'api_test_email'))

    def testGenerateToken(self):
        user_id = connection.execute(create_auth_user(
            email='api_test_email')).inserted_primary_key[0]
        token_res = api.user.generate_token(connection,
                                            {'email': 'api_test_email'})
        response = token_res['result']
        user = get_auth_user(connection, user_id)
        self.assertTrue(bcrypt_sha256.verify(response['token'], user.token))
        self.assertEqual(response['expires_on'][:10],
                         str((datetime.now() + timedelta(days=60)).date()))

    def testGenerateTokenWithDuration(self):
        user_id = connection.execute(create_auth_user(
            email='api_test_email')).inserted_primary_key[0]
        response = api.user.generate_token(connection,
                                           {'email': 'api_test_email',
                                            'duration': 5.0})['result']
        user = get_auth_user(connection, auth_user_id=user_id)
        self.assertTrue(bcrypt_sha256.verify(response['token'], user.token))
        self.assertEqual(response['expires_on'][:10],
                         str(datetime.now().date()))

    def testTokenDurationTooLong(self):
        connection.execute(create_auth_user(email='api_test_email'))
        self.assertRaises(api.user.TokenDurationTooLong,
                          api.user.generate_token,
                          connection,
                          {'email': 'api_test_email',
                           'duration': 999999999999999})


class TestUser(unittest.TestCase):
    def tearDown(self):
        connection.execute(auth_user_table.delete().where(
            auth_user_table.c.email == 'api_user_test_email'))

    def testCreateUser(self):
        expected = {'result': {'email': 'api_user_test_email',
                               'response': 'Created'}}
        self.assertEqual(
            api.user.create_user(connection, {'email': 'api_user_test_email'}),
            expected)

        expected2 = {'result': {'email': 'api_user_test_email',
                                'response': 'Already exists'}}

        self.assertEqual(
            api.user.create_user(connection, {'email': 'api_user_test_email'}),
            expected2)


class TestAggregation(unittest.TestCase):
    def tearDown(self):
        connection.execute(submission_table.delete())

    def testMin(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        question_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(connection, input_data)

        expected = {'result': 0, 'query': 'min'}

        self.assertEqual(
            api.aggregation.min(connection, question_id, email='test_email'),
            expected)
        user_id = get_auth_user_by_email(connection, 'test_email').auth_user_id
        self.assertEqual(
            api.aggregation.min(connection, question_id, auth_user_id=user_id),
            expected)

    def testMinNoUser(self):
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        self.assertRaises(TypeError, api.aggregation.min, connection,
                          question_id)

    def testMinWrongUser(self):
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        self.assertRaises(QuestionDoesNotExistError, api.aggregation.min,
                          connection,
                          question_id, email='a.dahir7@gmail.com')

    def testMinNoSubmissions(self):
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        self.assertRaises(api.aggregation.NoSubmissionsToQuestionError,
                          api.aggregation.min, connection, question_id,
                          email='test_email')

    def testMinInvalidType(self):
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'text')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        self.assertRaises(api.aggregation.InvalidTypeForAggregationError,
                          api.aggregation.min, connection, question_id,
                          email='test_email')

    def testMax(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        question_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(connection, input_data)

        self.assertEqual(
            api.aggregation.max(connection, question_id, email='test_email'),
            {'result': 1, 'query': 'max'})

    def testMinMaxDate(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'date')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        question_id = question.question_id

        for i in range(1, 3):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': question_id,
                                'answer': '1/{}/2015'.format(i),
                                'is_other': False}]}
            api.submission.submit(connection, input_data)

        self.assertEqual(
            api.aggregation.max(connection, question_id, email='test_email'),
            {'result': str(date(2015, 1, 2)), 'query': 'max'})
        self.assertEqual(
            api.aggregation.min(connection, question_id, email='test_email'),
            {'result': str(date(2015, 1, 1)), 'query': 'min'})

    def testSum(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        question_id = question.question_id

        for i in range(-4, 4):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(connection, input_data)

        self.assertEqual(
            api.aggregation.sum(connection, question_id, email='test_email'),
            {'result': -4, 'query': 'sum'})

    def testCount(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        question_id = question.question_id

        self.assertEqual(
            api.aggregation.count(connection, question_id, email='test_email'),
            {'result': 0, 'query': 'count'})

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(connection, input_data)

        self.assertEqual(
            api.aggregation.count(connection, question_id, email='test_email'),
            {'result': 2, 'query': 'count'})

    def testCountOther(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        question_id = question.question_id

        self.assertEqual(
            api.aggregation.count(connection, question_id, email='test_email'),
            {'result': 0, 'query': 'count'})

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': question_id,
                                'answer': str(i),
                                'is_other': True}]}
            api.submission.submit(connection, input_data)

        self.assertEqual(
            api.aggregation.count(connection, question_id, email='test_email'),
            {'result': 2, 'query': 'count'})

    def testCountMultipleChoice(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        cond = and_(question_table.c.survey_id == survey_id,
                    question_table.c.type_constraint_name == 'multiple_choice')
        q_where = question_table.select().where(cond)
        question = connection.execute(q_where).first()
        question_id = question.question_id

        self.assertEqual(
            api.aggregation.count(connection, question_id, email='test_email'),
            {'result': 0, 'query': 'count'})

        for choice in get_choices(connection, question_id):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': question_id,
                                'answer': choice.question_choice_id,
                                'is_other': False}]}
            api.submission.submit(connection, input_data)

        self.assertEqual(
            api.aggregation.count(connection, question_id, email='test_email'),
            {'result': 2, 'query': 'count'})

    def testAvg(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        question_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(connection, input_data)

        self.assertAlmostEqual(
            api.aggregation.avg(connection,
                                question_id,
                                email='test_email')['result'],
            0.5)

    def testStddevPop(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        for i in range(3):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(connection, input_data)

        expected_value = sqrt(sum((i - 1) ** 2 for i in range(3)) / 3)
        self.assertAlmostEqual(
            api.aggregation.stddev_pop(connection, q_id, email='test_email')[
                'result'],
            expected_value)

    def testStddevSamp(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        for i in range(3):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(connection, input_data)

        self.assertAlmostEqual(
            api.aggregation.stddev_samp(connection, q_id, email='test_email')[
                'result'],
            1)

    def testMode(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        for i in (1, 2, 2, 2, 3, 3, 3):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(connection, input_data)

        self.assertListEqual(
            api.aggregation.mode(connection, q_id, email='test_email')[
                'result'], [2, 3])

        self.assertListEqual(
            api.aggregation.mode(connection, q_id,
                                 auth_user_id=get_auth_user_by_email(
                                     connection,
                                     'test_email').auth_user_id)['result'],
            [2, 3])

    def testModeDecimal(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'decimal')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        for i in (1, 2, 2, 2, 3, 3):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(connection, input_data)

        self.assertEqual(
            api.aggregation.mode(connection, q_id, email='test_email'),
            {'result': [2], 'query': 'mode'})

        self.assertEqual(
            api.aggregation.mode(connection, q_id,
                                 auth_user_id=get_auth_user_by_email(
                                     connection,
                                     'test_email').auth_user_id),
            {'result': [2], 'query': 'mode'})

    def testModeLocation(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'location')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        for i in (1, 2, 2, 2, 3, 3):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': q_id,
                                'answer': [i, i],
                                'is_other': False}]}
            api.submission.submit(connection, input_data)

        self.assertEqual(
            api.aggregation.mode(connection, q_id, email='test_email'),
            {'result': [[2, 2]], 'query': 'mode'})

        self.assertEqual(
            api.aggregation.mode(connection, q_id,
                                 auth_user_id=get_auth_user_by_email(
                                     connection,
                                     'test_email').auth_user_id),
            {'result': [[2, 2]], 'query': 'mode'})

    def testModeBadeType(self):
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'note')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        self.assertRaises(api.aggregation.InvalidTypeForAggregationError,
                          api.aggregation.mode, connection, question_id,
                          email='test_email')

    def testModeMultipleChoice(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first(
        ).survey_id
        cond = and_(question_table.c.survey_id == survey_id,
                    question_table.c.type_constraint_name ==
                    'multiple_choice')
        q_where = question_table.select().where(cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        self.assertEqual(
            api.aggregation.count(connection, q_id, email='test_email'),
            {'result': 0, 'query': 'count'})

        for choice in get_choices(connection, q_id):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': q_id,
                                'answer': choice.question_choice_id,
                                'is_other': False}]}
            api.submission.submit(connection, input_data)
        repeated_choice = get_choices(connection,
                                      q_id).first().question_choice_id
        input_data = {'survey_id': survey_id,
                      'submitter': 'test_submitter',
                      'answers':
                          [{'question_id': q_id,
                            'answer': repeated_choice,
                            'is_other': False}]}
        api.submission.submit(connection, input_data)

        self.assertEqual(
            api.aggregation.mode(connection, q_id, email='test_email'),
            {'result': [get_choices(connection, q_id).first().choice],
             'query': 'mode'})

    def testTimeSeries(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        for i in range(3):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(connection, input_data)

        res = \
            api.aggregation.time_series(connection, q_id, email='test_email')[
                'result']
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0][1], 0)
        self.assertEqual(res[1][1], 1)
        self.assertEqual(res[2][1], 2)

    def testBarGraph(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        for i in [0, 2, 1, 0]:
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(connection, input_data)

        res = api.aggregation.bar_graph(connection, q_id, email='test_email')
        self.assertEqual(res, {'result': [[0, 2], [1, 1], [2, 1]],
                               'query': 'bar_graph'})

    def testGetQuestionStats(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        self.assertGreater(len(
            api.aggregation.get_question_stats(connection, survey_id,
                                               email='test_email')), 0)


if __name__ == '__main__':
    unittest.main()
