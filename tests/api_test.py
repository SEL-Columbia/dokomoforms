"""
Tests for the dokomo JSON api

"""
import unittest
import uuid
from sqlalchemy import and_
from datetime import datetime, timedelta

from sqlalchemy.exc import DataError, IntegrityError
from passlib.hash import bcrypt_sha256

from api import execute_with_exceptions
import api.survey
import api.submission
import api.user
import db
from db.answer import answer_insert, CannotAnswerMultipleTimesError, \
    get_answers
from db.answer_choice import get_answer_choices
from db.auth_user import auth_user_table, create_auth_user, get_auth_user
from db.question import question_table, get_questions, \
    QuestionDoesNotExistError, MissingMinimalLogicError
from db.question_branch import get_branches, MultipleBranchError
from db.question_choice import question_choice_table, get_choices, \
    RepeatedChoiceError, QuestionChoiceDoesNotExistError
from db.submission import submission_table, submission_insert, \
    SubmissionDoesNotExistError, submission_select, get_submissions_by_email
from db.survey import survey_table, survey_select, SurveyDoesNotExistError
from db.type_constraint import TypeConstraintDoesNotExistError


class TestSubmission(unittest.TestCase):
    def tearDown(self):
        submission_table.delete().execute()
        survey_table.delete().where(
            survey_table.c.title.in_(('survey with required question',
            ))).execute()

    def testSubmit(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        question_id = question_table.select().where(
            and_cond).execute().first().question_id
        second_cond = and_(question_table.c.survey_id == survey_id,
                           question_table.c.type_constraint_name ==
                           'multiple_choice')
        second_q_id = question_table.select().where(
            second_cond).execute().first().question_id
        choice_cond = question_choice_table.c.question_id == second_q_id
        choice_id = question_choice_table.select().where(
            choice_cond).execute().first().question_choice_id
        third_cond = and_(question_table.c.survey_id == survey_id,
                          question_table.c.type_constraint_name == 'text')
        third_q_id = question_table.select().where(
            third_cond).execute().first().question_id
        fourth_cond = and_(question_table.c.survey_id == survey_id,
                           question_table.c.type_constraint_name == 'decimal')
        fourth_q_id = question_table.select().where(
            fourth_cond).execute().first().question_id
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
        response = api.submission.submit(input_data)
        submission_id = response['submission_id']
        condition = submission_table.c.submission_id == submission_id
        self.assertEqual(
            submission_table.select().where(condition).execute().rowcount, 1)
        data = api.submission.get_one(submission_id, email='test_email')
        self.assertEqual(response, data)
        self.assertEqual(data['answers'][0]['answer'], 1)
        self.assertEqual(data['answers'][1]['answer'], choice_id)
        self.assertEqual(data['answers'][2]['answer'], 3.5)
        self.assertEqual(data['answers'][3]['answer'], 'answer one')
        self.assertEqual(data['answers'][4]['answer'], 'answer two')

    def testIncorrectType(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        question_id = question_table.select().where(
            and_cond).execute().first().question_id
        input_data = {'submitter': 'me',
                      'survey_id': survey_id,
                      'answers':
                          [{'question_id': question_id,
                            'answer': 'one',
                            'is_other': False}]}
        self.assertRaises(DataError, api.submission.submit, input_data)
        self.assertEqual(submission_table.select().execute().rowcount, 0)

    def testSkippedQuestion(self):
        questions = [{'title': 'required question',
                      'type_constraint_name': 'integer',
                      'sequence_number': None,
                      'question_to_sequence_number': 1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': True, 'with_other': False},
                      'choices': None,
                      'branches': None}]
        data = {'title': 'survey with required question',
                'questions': questions,
                'email': 'test_email'}
        survey = api.survey.create(data)
        survey_id = survey['survey_id']

        submission = {'submitter': 'me',
                      'survey_id': survey_id,
                      'answers': []}
        self.assertRaises(api.submission.RequiredQuestionSkippedError,
                          api.submission.submit, submission)

        question_id = survey['questions'][0]['question_id']

        submission2 = {'submitter': 'me',
                       'survey_id': survey_id,
                       'answers': [{'question_id': question_id,
                                    'answer': None}]}

        self.assertRaises(api.submission.RequiredQuestionSkippedError,
                          api.submission.submit, submission2)

    def testQuestionDoesNotExist(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        input_data = {'submitter': 'me',
                      'survey_id': survey_id,
                      'answers': [{'question_id': str(uuid.uuid4()),
                                   'answer': 1}]}
        self.assertRaises(QuestionDoesNotExistError, api.submission.submit,
                          input_data)

    def testSurveyDoesNotExist(self):
        survey_id = str(uuid.uuid4())
        input_data = {'submitter': 'me', 'survey_id': survey_id, 'answers': []}
        self.assertRaises(SurveyDoesNotExistError, api.submission.submit,
                          input_data)

    def testDateAndTime(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        date_cond = and_(question_table.c.survey_id == survey_id,
                         question_table.c.type_constraint_name == 'date')
        date_question_id = question_table.select().where(
            date_cond).execute().first().question_id
        time_cond = and_(question_table.c.survey_id == survey_id,
                         question_table.c.type_constraint_name == 'time')
        time_question_id = question_table.select().where(
            time_cond).execute().first().question_id
        input_data = {'submitter': 'me',
                      'survey_id': survey_id,
                      'answers':
                          [{'question_id': date_question_id,
                            'answer': '2014-10-27',
                            'is_other': False},
                           {'question_id': time_question_id,
                            'answer': '11:26-04:00',
                            'is_other': False}]}  # UTC-04:00
        response = api.submission.submit(input_data)
        self.assertEqual(response['answers'][0]['answer'], '2014-10-27')
        self.assertEqual(response['answers'][1]['answer'], '11:26:00-04:00')

    def testMultipleAnswersNotAllowed(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        question_id = question_table.select().where(
            and_cond).execute().first().question_id
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
                          input_data)


    def testGet(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'location')
        question = q_where.execute().first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = submission_insert(submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        answer_insert(answer=[90, 0], question_id=question_id,
                      submission_id=submission_id,
                      survey_id=survey_id, type_constraint_name=tcn,
                      sequence_number=seq, allow_multiple=mul).execute()
        data = api.submission.get_one(submission_id, email='test_email')
        self.assertIsNotNone(data['submission_id'])
        self.assertIsNotNone(data['answers'])

    def testGetForSurvey(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question = q_where.execute().first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        for i in range(2):
            submission_exec = submission_insert(submitter='test_submitter',
                                                survey_id=survey_id).execute()
            submission_id = submission_exec.inserted_primary_key[0]
            answer_insert(answer=i, question_id=question_id,
                          submission_id=submission_id,
                          survey_id=survey_id, type_constraint_name=tcn,
                          sequence_number=seq, allow_multiple=mul).execute()
        data = api.submission.get_all(survey_id, email='test_email')
        self.assertGreater(len(data), 0)

    def testDelete(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        data = {'submitter': 'me',
                'survey_id': survey_id,
                'answers': [{'answer': None}]}
        submission_id = api.submission.submit(data)['submission_id']
        api.submission.delete(submission_id)
        self.assertRaises(SubmissionDoesNotExistError,
                          submission_select,
                          submission_id,
                          email='test_email')


class TestSurvey(unittest.TestCase):
    def tearDown(self):
        survey_table.delete().where(
            survey_table.c.title.in_(('updated',
            ))).execute()
        survey_table.delete().where(
            survey_table.c.title.like('to_be_updated%')).execute()
        survey_table.delete().where(
            survey_table.c.title.like('bad update survey%')).execute()
        survey_table.delete().where(
            survey_table.c.title.like('api_test survey%')).execute()
        survey_table.delete().where(
            survey_table.c.title.like('test_title(%')).execute()
        survey_table.delete().where(
            survey_table.c.title.like('updated survey title%')).execute()
        survey_table.delete().where(
            survey_table.c.title.like('not in conflict%')).execute()
        submission_table.delete().execute()

    def testGetOne(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        data = api.survey.get_one(survey_id, email='test_email')
        self.assertIsNotNone(data['survey_id'])
        self.assertIsNotNone(data['questions'])

    def testDisplaySurvey(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        data = api.survey.display_survey(survey_id)
        self.assertIsNotNone(data['survey_id'])
        self.assertIsNotNone(data['questions'])

    def testGetAll(self):
        email = auth_user_table.select().where(
            auth_user_table.c.email == 'test_email').execute().first().email
        surveys = api.survey.get_all(email)
        self.assertGreater(len(surveys), 0)

    def testCreate(self):
        questions = [{'title': 'api_test mc question',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': ['choice 1', 'choice 2'],
                      'branches': [{'choice_number': 0,
                                    'to_question_number': 1}]
                     },
                     {'title': 'api_test question',
                      'type_constraint_name': 'text',
                      'sequence_number': None,
                      'question_to_sequence_number': 1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False,
                                'with_other': False,
                                'min': 3},
                      'choices': None,
                      'branches': None}]
        data = {'title': 'api_test survey',
                'questions': questions,
                'email': 'test_email'}
        survey_id = api.survey.create(data)['survey_id']
        condition = survey_table.c.survey_id == survey_id
        self.assertEqual(
            survey_table.select().where(condition).execute().rowcount, 1)
        questions = list(get_questions(survey_id))
        self.assertEqual(questions[1].logic,
                         {'required': False, 'with_other': False, 'min': 3})
        self.assertEqual(get_choices(questions[0].question_id).first().choice,
                         'choice 1')

    def testLogicMissing(self):
        questions = [{'title': 'api_test mc question',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {},
                      'choices': ['choice 1', 'choice 2'],
                      'branches': [{'choice_number': 0,
                                    'to_question_number': 1}]
                     }]
        data = {'title': 'api_test survey',
                'questions': questions,
                'email': 'test_email'}
        self.assertRaises(MissingMinimalLogicError, api.survey.create, data)


    def testSurveyAlreadyExists(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        title = survey_select(survey_id, email='test_email').title
        input_data = {'title': title, 'questions': [], 'email': 'test_email'}
        result = api.survey.create(input_data)
        self.assertEqual(result['title'], 'test_title(1)')
        result2 = api.survey.create(input_data)
        self.assertEqual(result2['title'], 'test_title(2)')
        result3 = api.survey.create(
            {'title': 'test_title(1)', 'questions': [], 'email': 'test_email'})
        self.assertEqual(result3['title'], 'test_title(1)(1)')

        api.survey.create({'title': 'not in conflict(1)',
                           'questions': [],
                           'email': 'test_email'})
        result4 = api.survey.create({'title': 'not in conflict',
                                     'questions': [],
                                     'email': 'test_email'})
        self.assertEqual(result4['title'], 'not in conflict')

    def testTwoChoicesWithSameName(self):
        input_data = {'title': 'choice error',
                      'email': 'test_email',
                      'questions': [{'title': 'choice error',
                                     'type_constraint_name': 'multiple_choice',
                                     'sequence_number': None,
                                     'question_to_sequence_number': 1,
                                     'hint': None,
                                     'allow_multiple': False,
                                     'logic': {'required': False,
                                               'with_other': False},
                                     'choices': ['a', 'a']}]}
        self.assertRaises(RepeatedChoiceError, api.survey.create, input_data)

    def testTwoBranchesFromOneChoice(self):
        input_data = {'title': 'choice error',
                      'email': 'test_email',
                      'questions': [{'title': 'choice error',
                                     'type_constraint_name': 'multiple_choice',
                                     'sequence_number': None,
                                     'question_to_sequence_number': 1,
                                     'hint': None,
                                     'allow_multiple': False,
                                     'logic': {'required': False,
                                               'with_other': False},
                                     'choices': ['a', 'b'],
                                     'branches': [{'choice_number': 0,
                                                   'to_question_number': 1},
                                                  {'choice_number': 0,
                                                   'to_question_number': 2}]},
                                    {'title': 'choice error',
                                     'type_constraint_name': 'text',
                                     'sequence_number': None,
                                     'question_to_sequence_number': 1,
                                     'hint': None,
                                     'allow_multiple': False,
                                     'logic': {'required': False,
                                               'with_other': False},
                                     'choices': None,
                                     'branches': None},
                                    {'title': 'choice error',
                                     'type_constraint_name': 'text',
                                     'sequence_number': None,
                                     'question_to_sequence_number': 1,
                                     'hint': None,
                                     'allow_multiple': False,
                                     'logic': {'required': False,
                                               'with_other': False},
                                     'choices': None,
                                     'branches': None}]}
        self.assertRaises(MultipleBranchError, api.survey.create, input_data)

    def testTypeConstraintDoesNotExist(self):
        input_data = {'title': 'type constraint error',
                      'email': 'test_email',
                      'questions': [{'title': 'type constraint error',
                                     'type_constraint_name': 'not real',
                                     'sequence_number': None,
                                     'question_to_sequence_number': 1,
                                     'hint': None,
                                     'allow_multiple': False,
                                     'logic': {'required': False,
                                               'with_other': False}}]}
        self.assertRaises(TypeConstraintDoesNotExistError, api.survey.create,
                          input_data)
        condition = survey_table.c.title == 'type constraint error'
        self.assertEqual(
            survey_table.select().where(condition).execute().rowcount, 0)

    def testUpdate(self):
        questions = [{'title': 'api_test question',
                      'type_constraint_name': 'text',
                      'sequence_number': None,
                      'question_to_sequence_number': 1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': [],
                      'branches': []},
                     {'title': 'api_test 2nd question',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': ['1', '2', '3'],
                      'branches': [
                          {'choice_number': 0, 'to_question_number': 2}]},
                     {'title': 'api_test 3rd question',
                      'type_constraint_name': 'text',
                      'sequence_number': None,
                      'question_to_sequence_number': 1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': [],
                      'branches': []}]
        data = {'title': 'api_test survey',
                'questions': questions,
                'email': 'test_email'}
        survey_id = api.survey.create(data)['survey_id']
        inserted_qs = get_questions(survey_id).fetchall()
        choice_1 = get_choices(inserted_qs[1].question_id).fetchall()[0]
        choice_1_id = choice_1.question_choice_id

        submission = {'submitter': 'me',
                      'survey_id': survey_id,
                      'answers': [{'question_id': inserted_qs[0].question_id,
                                   'answer': 'text answer',
                                   'is_other': False},
                                  {'question_id': inserted_qs[1].question_id,
                                   'answer': choice_1_id,
                                   'is_other': False}]}
        api.submission.submit(submission)

        update_json = {'survey_id': survey_id,
                       'title': 'updated survey title',
                       'email': 'test_email'}
        questions = [{'question_id': inserted_qs[1].question_id,
                      'title': 'api_test 2nd question',
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
                          {'choice_number': 1, 'to_question_number': 2}]},
                     {'question_id': inserted_qs[0].question_id,
                      'title': 'updated question title',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'type_constraint_name': 'text',
                      'question_to_sequence_number': 1,
                      'choices': [],
                      'branches': []},
                     {'title': 'second question',
                      'type_constraint_name': 'integer',
                      'sequence_number': None,
                      'question_to_sequence_number': 1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': [],
                      'branches': []}]
        update_json['questions'] = questions
        new_survey = api.survey.update(update_json)
        new_survey_id = new_survey['survey_id']
        upd_survey = survey_select(new_survey_id, email='test_email')
        upd_questions = get_questions(new_survey_id).fetchall()
        branch = get_branches(upd_questions[0].question_id).first()
        self.assertEqual(branch.to_question_id, upd_questions[2].question_id)
        self.assertEqual(upd_questions[0].title, 'api_test 2nd question')
        self.assertEqual(upd_questions[0].logic,
                         {'required': False,
                          'with_other': False,
                          'max': 'one'})
        self.assertEqual(upd_survey.title, 'updated survey title')
        self.assertEqual(upd_questions[1].title, 'updated question title')
        choices = get_choices(upd_questions[0].question_id).fetchall()
        self.assertEqual(choices[0].choice, 'b')
        self.assertEqual(choices[1].choice, 'a')
        self.assertEqual(choices[2].choice, '1')
        self.assertEqual(len(choices), 3)
        new_submission = get_submissions_by_email(new_survey_id,
                                                  email='test_email').first()
        text_answer = get_answers(new_submission.submission_id).first()
        self.assertEqual(text_answer.answer_text, 'text answer')
        the_choice = get_answer_choices(new_submission.submission_id).first()
        self.assertEqual(the_choice.question_choice_id,
                         choices[2].question_choice_id)

    def testUpdateTypeConstraintChange(self):
        questions = [{'title': 'was text question',
                      'type_constraint_name': 'text',
                      'sequence_number': None,
                      'question_to_sequence_number': 2,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': [],
                      'branches': []},
                     {'title': 'was multiple choice',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 3,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': ['1', '2', '3'],
                      'branches': []},
                     {'title': 'was multiple choice 2',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 4,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': ['a', 'b', 'c'],
                      'branches': []},
                     {'title': 'was with other',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 5,
                      'hint': None,
                      'allow_multiple': True,
                      'logic': {'required': False, 'with_other': True},
                      'choices': ['use other'],
                      'branches': []},
                     {'title': 'was with other 2',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 6,
                      'hint': None,
                      'allow_multiple': True,
                      'logic': {'required': False, 'with_other': True},
                      'choices': ['use other 2'],
                      'branches': []},
                     {'title': 'was with other, lose choices',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 7,
                      'hint': None,
                      'allow_multiple': True,
                      'logic': {'required': False, 'with_other': True},
                      'choices': ['use other 3'],
                      'branches': []}]
        data = {'title': 'to_be_updated',
                'questions': questions,
                'email': 'test_email'}
        survey_id = api.survey.create(data)['survey_id']
        inserted_qs = get_questions(survey_id).fetchall()
        choice_1 = get_choices(inserted_qs[1].question_id).first()
        choice_1_id = choice_1.question_choice_id
        choice_a = get_choices(inserted_qs[2].question_id).first()
        choice_a_id = choice_a.question_choice_id
        other_choice = get_choices(inserted_qs[3].question_id).first()
        other_choice_id = other_choice.question_choice_id
        other_choice_2 = get_choices(inserted_qs[4].question_id).first()
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

        api.submission.submit(submission)

        update_json = {'survey_id': survey_id,
                       'title': 'updated',
                       'email': 'test_email'}
        questions = [{'question_id': inserted_qs[0].question_id,
                      'title': 'was text question, now multiple_choice',
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': 1,
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'choices': [],
                      'branches': []},
                     {'question_id': inserted_qs[1].question_id,
                      'title': 'was multiple choice, now location',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'type_constraint_name': 'location',
                      'question_to_sequence_number': 1,
                      'choices': [],
                      'branches': []},
                     {'question_id': inserted_qs[2].question_id,
                      'title': 'was multiple choice, now with other',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': True},
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': 1,
                      'choices': ['a'],
                      'branches': []},
                     {'question_id': inserted_qs[3].question_id,
                      'title': 'lost with other',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': 1,
                      'choices': ['use other'],
                      'branches': []},
                     {'question_id': inserted_qs[4].question_id,
                      'title': 'lost with other 2',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'type_constraint_name': 'text',
                      'question_to_sequence_number': 1,
                      'choices': [],
                      'branches': []},
                     {'question_id': inserted_qs[4].question_id,
                      'title': 'lost choices',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': True},
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': 1,
                      'choices': [],
                      'branches': []}]
        update_json['questions'] = questions
        new_survey = api.survey.update(update_json)
        new_submissions = get_submissions_by_email(new_survey['survey_id'],
                                                   email='test_email').fetchall()
        self.assertEqual(len(new_submissions), 1)
        choices = get_answer_choices(
            new_submissions[0].submission_id).fetchall()
        self.assertEqual(len(choices), 2)
        answers = get_answers(new_submissions[0].submission_id).fetchall()
        self.assertEqual(len(answers), 1)

    def testLyingAboutOther(self):
        questions = [{'title': 'really with other',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': True},
                      'choices': ['use other'],
                      'branches': []}]
        data = {'title': 'to_be_updated',
                'questions': questions,
                'email': 'test_email'}

        survey_id = api.survey.create(data)['survey_id']
        inserted_q_id = get_questions(survey_id).first().question_id

        submission = {'submitter': 'me',
                      'survey_id': survey_id,
                      'answers': [{'question_id': inserted_q_id,
                                   'answer': 'text answer',
                                   'is_other': False}]}

        self.assertRaises(DataError, api.submission.submit, submission)

    def testUpdateBadChoices(self):
        questions = [{'title': 'bad update question',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'question_to_sequence_number': 1,
                      'hint': None,
                      'allow_multiple': False,
                      'logic': {'required': False, 'with_other': False},
                      'choices': ['one', 'two'],
                      'branches': []}]
        data = {'title': 'bad update survey',
                'questions': questions,
                'email': 'test_email'}
        survey_id = api.survey.create(data)['survey_id']
        inserted_questions = get_questions(survey_id).fetchall()

        update_json = {'survey_id': survey_id,
                       'title': 'updated survey title',
                       'email': 'test_email'}
        questions = [{'question_id': inserted_questions[0].question_id,
                      'title': 'updated question title',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': 1,
                      'choices': ['two', 'one', 'one'],
                      'branches': []}]
        update_json['questions'] = questions
        self.assertRaises(RepeatedChoiceError, api.survey.update, update_json)

        questions = [{'question_id': inserted_questions[0].question_id,
                      'title': 'updated question title',
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
                          update_json)

        questions = [{'question_id': inserted_questions[0].question_id,
                      'title': 'updated question title',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': 1,
                      'choices': [
                          {'old_choice': 'one', 'new_choice': 'two'}, 'two'],
                      'branches': []}]

        update_json['questions'] = questions
        self.assertRaises(RepeatedChoiceError, api.survey.update, update_json)

        questions = [{'question_id': inserted_questions[0].question_id,
                      'title': 'updated question title',
                      'allow_multiple': False,
                      'hint': None,
                      'logic': {'required': False, 'with_other': False},
                      'type_constraint_name': 'multiple_choice',
                      'question_to_sequence_number': 1,
                      'choices': [
                          {'old_choice': 'one', 'new_choice': 'two'},
                          {'old_choice': 'one', 'new_choice': 'three'}],
                      'branches': []}]

        update_json['questions'] = questions
        self.assertRaises(RepeatedChoiceError, api.survey.update, update_json)


    def testDelete(self):
        data = {'title': 'api_test survey',
                'questions': [],
                'email': 'test_email'}
        survey_id = api.survey.create(data)['survey_id']
        api.survey.delete(survey_id)
        self.assertRaises(SurveyDoesNotExistError, survey_select, survey_id,
                          email='test_email')


class TestUtils(unittest.TestCase):
    def testExecuteWithExceptions(self):
        executable = survey_table.insert({'title': ''})
        with db.engine.begin() as connection:
            self.assertRaises(ValueError, execute_with_exceptions, connection,
                              executable, [('null value', ValueError)])
        with db.engine.begin() as connection:
            self.assertRaises(IntegrityError, execute_with_exceptions,
                              connection, executable,
                              [('not in the error', ValueError)])


class TestAPIToken(unittest.TestCase):
    def tearDown(self):
        auth_user_table.delete().where(
            auth_user_table.c.email == 'api_test_email').execute()

    def testGenerateToken(self):
        user_id = create_auth_user(
            email='api_test_email').execute().inserted_primary_key[0]
        response = api.user.generate_token({'email': 'api_test_email'})
        user = get_auth_user(auth_user_id=user_id)
        self.assertTrue(bcrypt_sha256.verify(response['token'], user.token))
        self.assertEqual(response['expires_on'][:10],
                         str((datetime.now() + timedelta(days=60)).date()))

    def testGenerateTokenWithDuration(self):
        user_id = create_auth_user(
            email='api_test_email').execute().inserted_primary_key[0]
        response = api.user.generate_token({'email': 'api_test_email',
                                            'duration': 5.0})
        user = get_auth_user(auth_user_id=user_id)
        self.assertTrue(bcrypt_sha256.verify(response['token'], user.token))
        self.assertEqual(response['expires_on'][:10],
                         str(datetime.now().date()))

    def testTokenDurationTooLong(self):
        user_id = create_auth_user(
            email='api_test_email').execute().inserted_primary_key[0]
        self.assertRaises(api.user.TokenDurationTooLong,
                          api.user.generate_token,
                          {'email': 'api_test_email',
                           'duration': 999999999999999})


class TestUser(unittest.TestCase):
    def tearDown(self):
        auth_user_table.delete().where(
            auth_user_table.c.email == 'api_user_test_email').execute()

    def testCreateUser(self):
        self.assertEqual(
            api.user.create_user({'email': 'api_user_test_email'}),
            {'email': 'api_user_test_email', 'response': 'Created'})
        self.assertEqual(
            api.user.create_user({'email': 'api_user_test_email'}),
            {'email': 'api_user_test_email', 'response': 'Already exists'})


if __name__ == '__main__':
    unittest.main()

