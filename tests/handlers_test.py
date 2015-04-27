"""
Tests for the dokomo webapp

"""
from datetime import datetime

import unittest
from unittest import mock
from urllib.parse import urlencode, quote_plus
import uuid

from sqlalchemy import and_
from sqlalchemy import Table, MetaData
from tornado.escape import to_unicode, json_encode, json_decode
import tornado.gen
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.testing
from tornado.testing import AsyncHTTPTestCase
import tornado.web

from dokomoforms.api import json_response
import dokomoforms.api.aggregation as aggregation_api
import dokomoforms.api.submission as submission_api
import dokomoforms.api.survey as survey_api
import dokomoforms.api.user as user_api
from dokomoforms.db import engine
from dokomoforms import db
from dokomoforms.db.answer import get_answers
from dokomoforms.db.auth_user import generate_api_token, auth_user_table, \
    get_auth_user_by_email
from dokomoforms.db.question import get_questions_no_credentials, \
    question_table
from dokomoforms.db.question_choice import question_choice_table
from dokomoforms.db.submission import submission_table
from dokomoforms.handlers.api.aggregations import AggregationHandler
from dokomoforms.handlers.api.batch import BatchSubmissionAPIHandler
from dokomoforms.handlers.api.data_table import _base_query, \
    _apply_text_filter, \
    _get_orderings, _apply_ordering, _apply_limit, SurveyDataTableHandler, \
    SubmissionDataTableHandler, IndexSurveyDataTableHandler
from dokomoforms.handlers.api.submissions import SubmissionsAPIHandler, \
    SingleSubmissionAPIHandler, SubmissionActivityAPIHandler
from dokomoforms.handlers.api.surveys import SurveysAPIHandler, \
    SingleSurveyAPIHandler, SurveySubmissionsAPIHandler, SurveyStatsAPIHandler
from dokomoforms.handlers.auth import LoginHandler
from dokomoforms.handlers.util.base import catch_bare_integrity_error, \
    user_owns_question, APINoLoginHandler, iso_date_str_to_fmt_str
from dokomoforms.handlers.view.submissions import ViewSubmissionsHandler, \
    ViewSubmissionHandler
from dokomoforms.handlers.view.surveys import ViewHandler, ViewSurveyHandler
from dokomoforms.handlers.view.visualize import VisualizationHandler
from webapp import config, pages, Application
from dokomoforms.db.survey import survey_table


TEST_PORT = 8001  # just to show you can test the same
# container on a different port

POST_HDRS = {"Content-type": "application/x-www-form-urlencoded",
             "Accept": "text/plain"}

new_config = config.copy()
new_config['xsrf_cookies'] = False  # convenient for testing...

connection = db.engine.connect()


def _create_submission() -> dict:
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
    input_data = {'survey_id': survey_id,
                  'submitter': 'me',
                  'submitter_email': 'anon@anon.org',
                  'answers':
                      [{'question_id': question_id,
                        'answer': 1,
                        'answer_metadata': None,
                        'is_type_exception': False},
                       {'question_id': second_q_id,
                        'answer': choice_id,
                        'answer_metadata': None,
                        'is_type_exception': False},
                       {'question_id': third_q_id,
                        'answer': 'answer one',
                        'answer_metadata': None,
                        'is_type_exception': False},
                       {'question_id': third_q_id,
                        'answer': 'answer two',
                        'answer_metadata': None,
                        'is_type_exception': False},
                       {'question_id': fourth_q_id,
                        'answer': 3.5,
                        'answer_metadata': None,
                        'is_type_exception': False}]}
    return submission_api.submit(connection, input_data)['result']


class APITest(AsyncHTTPTestCase):
    def tearDown(self):
        connection.execute(submission_table.delete())
        connection.execute(survey_table.delete().where(
            survey_table.c.survey_title ==
            'survey_created_through_api'))

    def get_app(self):
        self.app = Application(pages, **new_config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def testGetSubmissionsNotLoggedIn(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        response = self.fetch('/api/surveys/{}/submissions'.format(survey_id))
        self.assertEqual(response.code, 403)

    def testGetSubmissionsLoggedIn(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        _create_submission()
        with mock.patch.object(SurveySubmissionsAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch(
                '/api/surveys/{}/submissions'.format(survey_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(
            webpage_response,
            submission_api.get_all(
                connection,
                'test_email',
                survey_id=survey_id
            )
        )

    def testGetSubmissionsBySubmitter(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        _create_submission()
        with mock.patch.object(SurveySubmissionsAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch(
                '/api/surveys/{}/submissions?submitter=me'.format(survey_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(
            webpage_response,
            submission_api.get_all(
                connection,
                'test_email',
                survey_id=survey_id,
                submitters=['me']
            )
        )

    def testGetSubmissionsWithFilter(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')

        question_id = connection.execute(question_table.select().where(
            and_cond)).first().question_id
        _create_submission()
        filters = [{'question_id': question_id, 'answer_integer': 1}]
        with mock.patch.object(SurveySubmissionsAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch(
                '/api/surveys/{}/submissions'.format(survey_id), method='POST',
                body=json_encode({'filters': filters}))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(
            webpage_response,
            submission_api.get_all(
                connection,
                'test_email',
                survey_id=survey_id,
                filters=filters
            )
        )

    def testGetSubmissionsWithAPIToken(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        token_result = user_api.generate_token(connection,
                                               {'email': 'test_email'})
        token = token_result['result']['token']
        response = self.fetch('/api/surveys/{}/submissions'.format(survey_id),
                              headers={'Token': token, 'Email': 'test_email'})
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json_decode(to_unicode(response.body)),
            submission_api.get_all(
                connection,
                'test_email',
                survey_id=survey_id
            )
        )

    def testGetSubmissionsWithoutAPIToken(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        response = self.fetch('/api/surveys/{}/submissions'.format(survey_id))
        self.assertEqual(response.code, 403)

    def testGetSubmissionsWithInvalidAPIToken(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        user_api.generate_token(connection, {'email': 'test_email'})
        response = self.fetch('/api/surveys/{}/submissions'.format(survey_id),
                              headers={'Token': generate_api_token(),
                                       'Email': 'test_email'})
        self.assertEqual(response.code, 403)

    def testGetSubmissionsGeneral(self):
        _create_submission()
        with mock.patch.object(SubmissionsAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/submissions')
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(
            webpage_response,
            submission_api.get_all(
                connection,
                'test_email'
            )
        )

    def testGetSubmissionsGeneralWithFilter(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')

        question_id = connection.execute(question_table.select().where(
            and_cond)).first().question_id
        _create_submission()
        filters = [{'question_id': question_id, 'answer_integer': 1}]
        with mock.patch.object(SubmissionsAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch(
                '/api/submissions?survey_id={}'.format(survey_id),
                method='POST',
                body=json_encode({'filters': filters}))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(
            webpage_response,
            submission_api.get_all(
                connection,
                'test_email',
                survey_id=survey_id,
                filters=filters
            )
        )

    def testGetSubmissionsGeneralBySubmitter(self):
        _create_submission()
        with mock.patch.object(SubmissionsAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/submissions?submitter=me')
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(
            webpage_response,
            submission_api.get_all(
                connection,
                'test_email',
                submitters=['me']
            )
        )

    def testGetActivityAllSurveys(self):
        _create_submission()
        with mock.patch.object(SubmissionActivityAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch(
                '/api/submissions/activity')
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(
            webpage_response,
            submission_api.get_activity(connection, 'test_email')
        )

    def testGetActivitySingleSurvey(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        _create_submission()
        with mock.patch.object(SubmissionActivityAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch(
                '/api/submissions/activity/{}'.format(survey_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(
            webpage_response,
            submission_api.get_activity(connection, 'test_email', survey_id)
        )

    def testGetSingleSubmission(self):
        submission_id = _create_submission()['submission_id']
        with mock.patch.object(SingleSubmissionAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/submissions/{}'.format(submission_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response,
                         submission_api.get_one(connection, submission_id,
                                                'test_email'))

    def testBatchSubmission(self):
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
        input_data = {
            'survey_id': survey_id,
            'submissions': [
                {'submitter': 'me',
                 'submitter_email': 'anon@anon.org',
                 'answers': [
                     {'question_id': question_id,
                      'answer': 1,
                      'answer_metadata': None,
                      'is_type_exception': False}]},
                {'submitter': 'me',
                 'submitter_email': 'anon@anon.org',
                 'answers': [
                     {'question_id': second_q_id,
                      'answer': choice_id,
                      'answer_metadata': None,
                      'is_type_exception': False}]},
            ]}

        token_result = user_api.generate_token(connection,
                                               {'email': 'test_email'})
        token = token_result['result']['token']

        with mock.patch.object(BatchSubmissionAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/batch/submit/{}'.format(survey_id),
                                  method='POST', body=json_encode(input_data),
                                  headers={'Email': 'test_email',
                                           'Token': token})
        result = json_decode(to_unicode(response.body))['result']
        self.assertEqual(len(result), 2)
        submission_1 = submission_api.get_one(
            connection, result[0], 'test_email')
        self.assertEqual(submission_1['result']['answers'][0]['answer'], 1)
        submission_2 = submission_api.get_one(
            connection, result[1], 'test_email')
        self.assertEqual(submission_2['result']['answers'][0]['answer'],
                         choice_id)
        self.assertEqual(response.code, 201)

    def testBatchSubmitMissingValue(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        answer_json = {'survey_id': survey_id}
        with mock.patch.object(BatchSubmissionAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/batch/submit/{}'.format(survey_id),
                                  method='POST',
                                  body=json_encode(answer_json))

        self.assertEqual(response.code, 422)
        self.assertIn('missing_field', str(response.error))

    def testBatchSubmitWrongSurveyID(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        wrong_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title != 'test_title')).first().survey_id
        answer_json = {
            'survey_id': wrong_id,
            'submissions': [
                {'submitter': 'me',
                 'submitter_email': 'anon@anon.org',
                 'answers': [
                     {'question_id': get_questions_no_credentials(
                         connection, survey_id).first().question_id,
                      'answer': 1,
                      'is_type_exception': False}]}
            ]
        }
        with mock.patch.object(BatchSubmissionAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/batch/submit/{}'.format(survey_id),
                                  method='POST',
                                  body=json_encode(answer_json))

        self.assertEqual(response.code, 422)
        self.assertIn('invalid', str(response.error))

    def testBatchSubmitWrongQuestionID(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        wrong_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title != 'test_title')).first().survey_id
        gqnc = get_questions_no_credentials
        question_id = gqnc(connection, wrong_id).first().question_id
        answers = [{'question_id': question_id,
                    'answer': 1,
                    'answer_metadata': None,
                    'is_type_exception': False}]
        answer_json = {
            'survey_id': survey_id,
            'submissions': [
                {'submitter': 'me',
                 'submitter_email': 'anon@anon.org',
                 'answers': answers},
            ]
        }
        with mock.patch.object(BatchSubmissionAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/batch/submit/{}'.format(survey_id),
                                  method='POST',
                                  body=json_encode(answer_json))

        self.assertEqual(response.code, 422)
        self.assertIn('invalid', str(response.error))

    def testGetSurveys(self):
        with mock.patch.object(SurveysAPIHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/surveys')
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response,
                         survey_api.get_all(connection, 'test_email'))

    def testGetSingleSurvey(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        with mock.patch.object(SingleSurveyAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/surveys/{}'.format(survey_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response,
                         survey_api.get_one(connection, survey_id,
                                            email='test_email'))

    def testCreateSurvey(self):
        input_data = {'email': 'test_email',
                      'survey_title': 'survey_created_through_api',
                      'survey_metadata': {},
                      'questions': [{'question_title': 'a question',
                                     'type_constraint_name': 'text',
                                     'hint': '',
                                     'allow_multiple': False,
                                     'logic': {
                                         'required': False,
                                         'allow_other': False,
                                         'allow_dont_know': False
                                     },
                                     'question_to_sequence_number': -1,
                                     'choices': None,
                                     'branches': None}]}

        token_result = user_api.generate_token(connection,
                                               {'email': 'test_email'})
        token = token_result['result']['token']

        response = self.fetch('/api/surveys/create',
                              method='POST', body=json_encode(input_data),
                              headers={'Email': 'test_email',
                                       'Token': token})
        result = json_decode(to_unicode(response.body))['result']
        survey_id = result['survey_id']
        self.assertEqual(result,
                         survey_api.get_one(connection, survey_id,
                                            email='test_email')['result'])
        self.assertEqual(response.code, 201)

    def testGetMin(self):
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
                          'submitter_email': 'anon@anon.org',
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'answer_metadata': None,
                                'is_type_exception': False}]}
            submission_api.submit(connection, input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?min'.format(question_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        min_res = aggregation_api.min(connection, question_id,
                                      email='test_email')
        self.assertEqual(webpage_response, json_response([min_res]))

    def testGetShmin(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        question_id = question.question_id

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch(
                '/api/aggregate/{}?shmin'.format(question_id))
        self.assertEqual(response.code, 422)
        self.assertIn('no_such_method', str(response.error))

    def testGetMinInvalidType(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'text')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        question_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'submitter_email': 'anon@anon.org',
                          'answers':
                              [{'question_id': question_id,
                                'answer': str(i),
                                'answer_metadata': None,
                                'is_type_exception': False}]}
            submission_api.submit(connection, input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?min'.format(question_id))
        self.assertEqual(response.code, 422)
        self.assertIn('invalid_type', str(response.error))

    def testGetMinNoSubmissions(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        question_id = question.question_id

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?min'.format(question_id))
        self.assertEqual(response.code, 422)
        self.assertIn('no_submissions', str(response.error))

    def testGetMax(self):
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
                          'submitter_email': 'anon@anon.org',
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'answer_metadata': None,
                                'is_type_exception': False}]}
            submission_api.submit(connection, input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?max'.format(question_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        max_res = aggregation_api.max(connection, question_id,
                                      email='test_email')
        self.assertEqual(webpage_response, json_response([max_res]))

    def testGetMinAndMax(self):
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
                          'submitter_email': 'anon@anon.org',
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'answer_metadata': None,
                                'is_type_exception': False}]}
            submission_api.submit(connection, input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch(
                '/api/aggregate/{}?min&max'.format(question_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))['result']
        self.assertNotEqual(webpage_response, [])
        self.assertIn(
            aggregation_api.min(connection, question_id, email='test_email'),
            webpage_response)
        self.assertIn(
            aggregation_api.max(connection, question_id, email='test_email'),
            webpage_response)

    def testGetSum(self):
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
                          'submitter_email': 'anon@anon.org',
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'answer_metadata': None,
                                'is_type_exception': False}]}
            submission_api.submit(connection, input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?sum'.format(question_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        sum_res = aggregation_api.sum(connection, question_id,
                                      email='test_email')
        self.assertEqual(webpage_response, json_response([sum_res]))

    def testGetCount(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'submitter_email': 'anon@anon.org',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'answer_metadata': None,
                                'is_type_exception': False}]}
            submission_api.submit(connection, input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?count'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response,
                         json_response([
                             aggregation_api.count(connection, q_id,
                                                   email='test_email')]))

    def testGetAvg(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'submitter_email': 'anon@anon.org',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'answer_metadata': None,
                                'is_type_exception': False}]}
            submission_api.submit(connection, input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?avg'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response,
                         json_response(
                             [aggregation_api.avg(connection, q_id,
                                                  email='test_email')]))

    def testGetStddevPop(self):
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
                          'submitter_email': 'anon@anon.org',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'answer_metadata': None,
                                'is_type_exception': False}]}
            submission_api.submit(connection, input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?stddev_pop'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        stddev_pop_res = aggregation_api.stddev_pop(connection, q_id,
                                                    email='test_email')
        self.assertEqual(webpage_response, json_response([stddev_pop_res]))

    def testGetStddevSamp(self):
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
                          'submitter_email': 'anon@anon.org',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'answer_metadata': None,
                                'is_type_exception': False}]}
            submission_api.submit(connection, input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?stddev_samp'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        stddev_samp_res = aggregation_api.stddev_samp(connection, q_id,
                                                      email='test_email')
        self.assertEqual(webpage_response, json_response([stddev_samp_res]))

    def testGetMode(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        for i in (1, 2, 2, 3):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'submitter_email': 'anon@anon.org',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'answer_metadata': None,
                                'is_type_exception': False}]}
            submission_api.submit(connection, input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?mode'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response,
                         json_response(
                             [aggregation_api.mode(connection, q_id,
                                                   email='test_email')]))

    def testGetModeLocation(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'location')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        input_data = {'survey_id': survey_id,
                      'submitter': 'test_submitter',
                      'submitter_email': 'anon@anon.org',
                      'answers':
                          [{'question_id': q_id,
                            'answer': {'lon': 90, 'lat': 0},
                            'answer_metadata': None,
                            'is_type_exception': False}]}
        submission_api.submit(connection, input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?mode'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response,
                         json_response(
                             [aggregation_api.mode(connection, q_id,
                                                   email='test_email')]))

    def testGetTimeSeries(self):
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
                          'submitter_email': 'anon@anon.org',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'answer_metadata': None,
                                'is_type_exception': False}]}
            submission_api.submit(connection, input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?time_series'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))['result']
        self.assertNotEqual(webpage_response, [])
        api_response = aggregation_api.time_series(connection, q_id,
                                                   email='test_email')
        self.assertSequenceEqual(webpage_response[0]['result'][0],
                                 api_response['result'][0])
        self.assertSequenceEqual(webpage_response[0]['result'][1],
                                 api_response['result'][1])

    def testGetBarGraph(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        for i in [0, 2, 1, 0]:
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'submitter_email': 'anon@anon.org',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'answer_metadata': None,
                                'is_type_exception': False}]}
            submission_api.submit(connection, input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?bar_graph'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))['result']
        self.assertNotEqual(webpage_response, [])
        api_response = aggregation_api.bar_graph(connection, q_id,
                                                 email='test_email')
        self.assertSequenceEqual(webpage_response[0]['result'][0],
                                 api_response['result'][0])
        self.assertSequenceEqual(webpage_response[0]['result'][1],
                                 api_response['result'][1])

    def testGetStats(self):
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
                          'submitter_email': 'anon@anon.org',
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'answer_metadata': None,
                                'is_type_exception': False}]}
            submission_api.submit(connection, input_data)

        with mock.patch.object(SurveyStatsAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/surveys/{}/stats'.format(survey_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        result = survey_api.get_stats(
            connection, survey_id, email='test_email'
        )
        self.assertEqual(webpage_response, result)


class APINoLoginTest(AsyncHTTPTestCase):
    def tearDown(self):
        connection.execute(submission_table.delete())

    def get_app(self):
        self.app = Application(pages, **config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def testPostSubmission(self):
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
        input_data = {'survey_id': survey_id,
                      'submitter': 'testPostSubmissionSubmitter',
                      'submitter_email': 'anon@anon.org',
                      'answers':
                          [{'question_id': question_id,
                            'answer': 1,
                            'answer_metadata': None,
                            'is_type_exception': False},
                           {'question_id': second_q_id,
                            'answer': choice_id,
                            'answer_metadata': None,
                            'is_type_exception': False},
                           {'question_id': third_q_id,
                            'answer': 'answer one',
                            'answer_metadata': None,
                            'is_type_exception': False},
                           {'question_id': third_q_id,
                            'answer': 'answer two',
                            'answer_metadata': None,
                            'is_type_exception': False},
                           {'question_id': fourth_q_id,
                            'answer': 3.5,
                            'answer_metadata': None,
                            'is_type_exception': False}]}

        token_result = user_api.generate_token(connection,
                                               {'email': 'test_email'})
        token = token_result['result']['token']

        with mock.patch.object(APINoLoginHandler, 'check_xsrf_cookie') as m:
            m.return_value = None
            response = self.fetch(
                '/api/surveys/{}/submit'.format(survey_id),
                method='POST',
                body=json_encode(input_data),
                headers={'Email': 'test_email', 'Token': token})
        result = json_decode(to_unicode(response.body))['result']
        submission_id = result['submission_id']
        self.assertEqual(result,
                         submission_api.get_one(connection, submission_id,
                                                email='test_email')['result'])
        self.assertEqual(response.code, 201)

    def testPostSubmissionNotJson(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id

        token_result = user_api.generate_token(connection,
                                               {'email': 'test_email'})
        token = token_result['result']['token']

        with mock.patch.object(APINoLoginHandler, 'check_xsrf_cookie') as m:
            m.return_value = None
            response = self.fetch(
                '/api/surveys/{}/submit'.format(survey_id),
                method='POST',
                body='not even close to json',
                headers={'Email': 'test_email', 'Token': token}
            )

        self.assertEqual(response.code, 400)
        self.assertEqual(str(response.error),
                         'HTTP 400: {"message": "Problems parsing JSON"}')

    def testPostSubmissionMissingValue(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        answer_json = {'survey_id': survey_id}

        token_result = user_api.generate_token(connection,
                                               {'email': 'test_email'})
        token = token_result['result']['token']

        with mock.patch.object(APINoLoginHandler, 'check_xsrf_cookie') as m:
            m.return_value = None
            response = self.fetch(
                '/api/surveys/{}/submit'.format(survey_id),
                method='POST',
                body=json_encode(answer_json),
                headers={'Email': 'test_email', 'Token': token}
            )

        self.assertEqual(response.code, 422)
        self.assertIn('missing_field', str(response.error))

    def testPostSubmissionWrongSurveyID(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        wrong_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title != 'test_title')).first().survey_id
        answer_json = {
            'survey_id': wrong_id,
            'answers': [
                {
                    'question_id': get_questions_no_credentials(
                        connection, survey_id).first().question_id,
                    'answer': 1,
                    'answer_metadata': None,
                    'is_type_exception': False
                }
            ]
        }

        token_result = user_api.generate_token(connection,
                                               {'email': 'test_email'})
        token = token_result['result']['token']

        with mock.patch.object(APINoLoginHandler, 'check_xsrf_cookie') as m:
            m.return_value = None
            response = self.fetch(
                '/api/surveys/{}/submit'.format(survey_id),
                method='POST',
                body=json_encode(answer_json),
                headers={'Email': 'test_email', 'Token': token}
            )

        self.assertEqual(response.code, 422)
        self.assertIn('invalid', str(response.error))

    def testPostSubmissionWrongQuestionID(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        wrong_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title != 'test_title')).first().survey_id
        gqnc = get_questions_no_credentials
        question_id = gqnc(connection, wrong_id).first().question_id
        answers = [{'question_id': question_id,
                    'answer': 1,
                    'answer_metadata': None,
                    'is_type_exception': False}]
        answer_json = {'submitter': 'me',
                       'submitter_email': 'anon@anon.org',
                       'survey_id': survey_id,
                       'answers': answers}

        token_result = user_api.generate_token(connection,
                                               {'email': 'test_email'})
        token = token_result['result']['token']

        with mock.patch.object(APINoLoginHandler, 'check_xsrf_cookie') as m:
            m.return_value = None
            response = self.fetch(
                '/api/surveys/{}/submit'.format(survey_id),
                method='POST',
                body=json_encode(answer_json),
                headers={'Email': 'test_email', 'Token': token}
            )

        self.assertEqual(response.code, 422)
        self.assertIn('invalid', str(response.error))

    def testPostSubmissionBadEmail(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        question_id = connection.execute(question_table.select().where(
            and_cond)).first().question_id

        answer_json = {
            'survey_id': survey_id,
            'submitter': 'testPostWithBadEmailSubmitter',
            'submitter_email': 'anon@anon.org',
            'answers':
                [{'question_id': question_id,
                  'answer': 1,
                  'answer_metadata': None,
                  'is_type_exception': False}]
        }

        token_result = user_api.generate_token(connection,
                                               {'email': 'test_email'})
        token = token_result['result']['token']

        with mock.patch.object(APINoLoginHandler, 'check_xsrf_cookie') as m:
            m.return_value = None
            response = self.fetch(
                '/api/surveys/{}/submit'.format(survey_id),
                method='POST',
                body=json_encode(answer_json),
                headers={'Email': 'a', 'Token': token}
            )

        self.assertEqual(response.code, 403)

    def testPostSubmissionBadHeaders(self):
        self.app = Application(pages, **config)

        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        question_id = connection.execute(question_table.select().where(
            and_cond)).first().question_id

        answer_json = {
            'survey_id': survey_id,
            'submitter': 'testPostWithBadToken',
            'submitter_email': 'anon@anon.org',
            'answers':
                [{'question_id': question_id,
                  'answer': 1,
                  'answer_metadata': None,
                  'is_type_exception': False}]
        }

        token_result = user_api.generate_token(connection,
                                               {'email': 'test_email'})
        token = token_result['result']['token']

        with mock.patch.object(APINoLoginHandler, 'check_xsrf_cookie') as m:
            m.return_value = None
            response = self.fetch(
                '/api/surveys/{}/submit'.format(survey_id),
                method='POST',
                body=json_encode(answer_json)
            )

        self.assertEqual(response.code, 201)


class DebugTest(AsyncHTTPTestCase):
    def get_app(self):
        self.app = Application(pages, **new_config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def tearDown(self):
        connection.execute(auth_user_table.delete().where(
            auth_user_table.c.email == 'debug_test_email'))

    def testCreate(self):
        self.fetch('/debug/create/debug_test_email')
        self.assertIsNotNone(
            get_auth_user_by_email(connection, 'debug_test_email'))

    def testLoginGet(self):
        response = self.fetch('/debug/login//')
        self.assertEqual(response.code, 200)

    def testLogin(self):
        response = self.fetch('/debug/login/test_email')
        self.assertIn('test_email', to_unicode(response.body))

    def testLoginFail(self):
        response = self.fetch('/debug/login/nope.avi')
        self.assertIn('No such user', to_unicode(response.body))

    def testLogout(self):
        response = self.fetch('/debug/logout')
        self.assertEqual(response.code, 200)


class BaseHandlerTest(AsyncHTTPTestCase):
    def get_app(self):
        self.app = Application(pages, **new_config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def testGet(self):
        response = self.fetch('/user/login/persona')
        self.assertEqual(response.code, 404)

    def testCatchBareIntegrityError(self):
        class Log():
            def error(self, dummy):
                pass

        table = Table('type_constraint', MetaData(bind=engine), autoload=True)
        wrapped = catch_bare_integrity_error(
            lambda: connection.execute(table.insert().values(
                type_constraint_name='text')), logger=Log())
        self.assertRaises(tornado.web.HTTPError, wrapped)

    def testUserOwnsQuestion(self):
        class UserDummy():
            current_user = 'test_email'
            db = connection

        def dummy(self, question_id):
            return True

        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()

        wrapped = user_owns_question(dummy)
        self.assertTrue(wrapped(UserDummy(), question.question_id))

        unauthorized = connection.execute(question_table.join(
            survey_table,
            question_table.c.survey_id == survey_table.c.survey_id
        ).join(
            auth_user_table,
            survey_table.c.auth_user_id == auth_user_table.c.auth_user_id
        ).select().where(auth_user_table.c.email != 'test_email')).first()

        self.assertRaises(tornado.web.HTTPError, wrapped, UserDummy(),
                          unauthorized.question_id)

    def testIsoDateStrToFmtStr(self):
        self.assertIsNone(iso_date_str_to_fmt_str(None, ''), None)
        result = iso_date_str_to_fmt_str(datetime.today().isoformat(), '%Y')
        self.assertEqual(int(result), datetime.today().year)


class AuthTest(AsyncHTTPTestCase):
    def get_app(self):
        self.app = Application(pages, **new_config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    @tornado.testing.gen_test
    def testAsyncPost(self):  # flake8: noqa
        con_dummy = lambda: None
        con_dummy.set_close_callback = lambda x: None
        dummy = lambda: None
        dummy.connection = con_dummy
        login = LoginHandler(self.app, dummy)
        response = yield login._async_post(
            tornado.httpclient.AsyncHTTPClient(), self.get_url('/'), '')
        self.assertEqual(response.code, 200)

    def testLoginSuccess(self):  # flake8: noqa
        with mock.patch.object(LoginHandler, '_async_post') as m:
            dummy = lambda: None
            dummy.body = json_encode({'status': 'okay', 'email': 'test_email'})
            m.return_value = tornado.gen.Task(
                lambda callback=None: callback(dummy))
            response = self.fetch(
                '/user/login/persona?assertion=woah', method='POST', body='')
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json_decode(response.body),
            {'next_url': '/', 'email': 'test_email'}
        )

    def testLoginFail(self):  # flake8: noqa
        with mock.patch.object(LoginHandler, '_async_post') as m:
            dummy = lambda: None
            dummy.body = json_encode(
                {'status': 'not okay', 'email': 'test_email'})
            m.return_value = tornado.gen.Task(
                lambda callback=None: callback(dummy))
            response = self.fetch(
                '/user/login/persona?assertion=woah', method='POST', body='')
        self.assertEqual(response.code, 400)


    def testLogout(self):
        response = self.fetch('/', method='POST', body='')
        self.assertEqual(response.code, 200)


class SurveyTest(AsyncHTTPTestCase):
    def get_app(self):
        self.app = Application(pages, **new_config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def tearDown(self):
        connection.execute(submission_table.delete())

    def testGetPrefix(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        response = self.fetch('/survey/{}'.format(survey_id[:35]))
        response2 = self.fetch('/survey/{}'.format(survey_id))
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, response2.body)

    def testGet(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        response = self.fetch('/survey/{}'.format(survey_id))
        self.assertEqual(response.code, 200)

    def testGet404(self):
        response = self.fetch('/survey/{}'.format(str(uuid.uuid4())))
        self.assertEqual(response.code, 404)


class ViewTest(AsyncHTTPTestCase):
    def tearDown(self):
        connection.execute(submission_table.delete())

    def get_app(self):
        self.app = Application(pages, **config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def testGetSurveys(self):
        with mock.patch.object(ViewHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/view')
        self.assertIn('table', to_unicode(response.body))

    def testGetSubmissions(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        _create_submission()
        with mock.patch.object(ViewSurveyHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/view/{}'.format(survey_id))
        self.assertIn('total-submissions">\n1', to_unicode(response.body))

    def testGetSubmission(self):
        submission_id = _create_submission()['submission_id']
        with mock.patch.object(ViewSubmissionHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/view/submission/{}'.format(submission_id))
        self.assertIn('3.5<br', to_unicode(response.body))


class VisualizationTest(AsyncHTTPTestCase):
    def tearDown(self):
        connection.execute(submission_table.delete())

    def get_app(self):
        self.app = Application(pages, **config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def testGetVisualizationForInteger(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        input_data = {'survey_id': survey_id,
                      'submitter': 'test_submitter',
                      'submitter_email': 'anon@anon.org',
                      'answers':
                          [{'question_id': q_id,
                            'answer': 1,
                            'answer_metadata': None,
                            'is_type_exception': False}]}
        submission_api.submit(connection, input_data)

        with mock.patch.object(VisualizationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/visualize/{}'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = to_unicode(response.body)
        self.assertIn('line_graph', webpage_response)
        self.assertIn('bar_graph', webpage_response)

    def testGetVisualizationsWithNoSubmissions(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        with mock.patch.object(VisualizationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/visualize/{}'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = to_unicode(response.body)
        self.assertIn('No viewable submissions.', webpage_response)

    def testGetVisualizationsForNote(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'note')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        with mock.patch.object(VisualizationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/visualize/{}'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = to_unicode(response.body)
        self.assertIn('No viewable submissions.', webpage_response)

    def testGetVisualizationForLocation(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'location')
        q_where = question_table.select().where(and_cond)
        question = connection.execute(q_where).first()
        q_id = question.question_id

        input_data = {'survey_id': survey_id,
                      'submitter': 'test_submitter',
                      'submitter_email': 'anon@anon.org',
                      'answers':
                          [{'question_id': q_id,
                            'answer': {'lon': 0, 'lat': 0},
                            'answer_metadata': None,
                            'is_type_exception': False}]}
        submission_api.submit(connection, input_data)

        with mock.patch.object(VisualizationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/visualize/{}'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = to_unicode(response.body)
        self.assertIn('bar_graph', webpage_response)
        self.assertIn('vis_map', webpage_response)


class DataTableTest(AsyncHTTPTestCase):
    def tearDown(self):
        connection.execute(submission_table.delete())

    def get_app(self):
        self.app = Application(pages, **config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def test_BaseQuery(self):
        query = _base_query(
            survey_table.join(auth_user_table),
            'a.dahir7@gmail.com',
            ['survey_title']
        )
        self.assertEqual(connection.execute(query).first()[1], 10)

    def test_BaseQueryWhere(self):
        query = _base_query(
            survey_table.join(auth_user_table),
            'a.dahir7@gmail.com',
            ['survey_title'],
            where=survey_table.c.survey_title.like('days%')
        )
        self.assertEqual(connection.execute(query).rowcount, 2)

    def test_ApplyTextFilter(self):
        query = _base_query(
            survey_table.join(auth_user_table),
            'a.dahir7@gmail.com',
            ['survey_title'],
        )
        query = _apply_text_filter(
            query,
            {'search': {'value': 'day'}},
            survey_table.c.survey_title
        )
        self.assertEqual(connection.execute(query).rowcount, 2)

    def test_getOrderings(self):
        args = {
            'order': [{'column': 1, 'dir': 'a'}, {'column': 0, 'dir': 'b'}],
            'columns': [{'name': 'c'}, {'name': 'd'}]
        }
        self.assertEqual(list(_get_orderings(args)), ['d a', 'c b'])

    def test_applyOrdering(self):
        query = _base_query(
            survey_table.join(auth_user_table),
            'a.dahir7@gmail.com',
            ['survey_title', 'created_on']
        )
        args = {
            'order': [
                {'column': 1, 'dir': 'desc'},
                {'column': 0, 'dir': 'asc'}
            ],
            'columns': [{'name': 'survey_title'}, {'name': 'created_on'}]
        }
        query = _apply_ordering(query, args, 'created_on', 'desc')
        result = connection.execute(query).fetchall()
        self.assertEqual(result[0]['survey_title'], 'days of the month')
        self.assertEqual(result[1]['survey_title'], 'days of the week')

    def test_applyLimit(self):
        query = _base_query(
            survey_table.join(auth_user_table),
            'a.dahir7@gmail.com',
            ['survey_title']
        )
        query = _apply_limit(query, {'length': 2})
        self.assertEqual(connection.execute(query).rowcount, 2)

    def test_applyLimitNoLimit(self):
        query = _base_query(
            survey_table.join(auth_user_table),
            'a.dahir7@gmail.com',
            ['survey_title']
        )
        query = _apply_limit(query, {'length': -1})
        self.assertEqual(connection.execute(query).rowcount, 10)

    def testGetSurveyDataTable(self):
        args = {
            'search': {
                'value': ''
            },
            'order': [],
            'length': 10,
            'draw': 1
        }
        urle = quote_plus(json_encode(args))
        with mock.patch.object(SurveyDataTableHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/survey_data_table?args=' + urle)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertEqual(webpage_response['recordsFiltered'], 1)
        self.assertEqual(webpage_response['draw'], 1)
        self.assertEqual(webpage_response['recordsTotal'], 1)
        data = webpage_response['data']
        self.assertEqual(data[0][0], 'test_title')
        self.assertEqual(data[0][-1], '0')

    def testGetSubmissionDataTable(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        _create_submission()
        args = {
            'search': {
                'value': ''
            },
            'order': [],
            'length': 10,
            'draw': 1
        }
        urle = quote_plus(json_encode(args))
        with mock.patch.object(SubmissionDataTableHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch(
                '/api/submission_data_table/{}?args='.format(survey_id) + urle
            )
        webpage_response = json_decode(to_unicode(response.body))
        self.assertEqual(webpage_response['recordsFiltered'], 1)
        self.assertEqual(webpage_response['draw'], 1)
        self.assertEqual(webpage_response['recordsTotal'], 1)
        data = webpage_response['data']
        self.assertEqual(data[0][1], 'me')

    def testGetIndexSurveyDataTable(self):
        args = {
            'search': {
                'value': ''
            },
            'order': [],
            'length': 10,
            'draw': 1
        }
        urle = quote_plus(json_encode(args))
        with mock.patch.object(IndexSurveyDataTableHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/index_survey_data_table?args=' + urle)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertEqual(webpage_response['recordsFiltered'], 1)
        self.assertEqual(webpage_response['draw'], 1)
        self.assertEqual(webpage_response['recordsTotal'], 1)
        data = webpage_response['data']
        self.assertEqual(data[0][0], 'test_title')
        self.assertEqual(data[0][1], '0')
        self.assertIsNone(data[0][2])


if __name__ == '__main__':
    unittest.main()
