"""
Tests for the dokomo webapp

"""

import unittest
from unittest import mock
from sqlalchemy import and_
import uuid
from sqlalchemy import Table, MetaData

from tornado.escape import to_unicode, json_encode, json_decode
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
from tornado.testing import AsyncHTTPTestCase
import tornado.web

from api import json_response
import api.aggregation
import api.submission
import api.survey
import api.user
from db import engine
from db.answer import get_answers
from db.auth_user import generate_api_token, auth_user_table, \
    get_auth_user_by_email
from db.question import get_questions_no_credentials, question_table
from db.question_choice import question_choice_table
from db.submission import submission_table
from pages.api.aggregations import AggregationHandler
from pages.api.submissions import SubmissionsAPIHandler, \
    SingleSubmissionAPIHandler
from pages.api.surveys import SurveysAPIHandler, SingleSurveyAPIHandler
from pages.util.base import catch_bare_integrity_error
from pages.view.submissions import ViewSubmissionsHandler, \
    ViewSubmissionHandler
from pages.view.surveys import ViewHandler
from webapp import config, pages
from db.survey import survey_table


TEST_PORT = 8001  # just to show you can test the same
# container on a different port

POST_HDRS = {"Content-type": "application/x-www-form-urlencoded",
             "Accept": "text/plain"}

new_config = config.copy()
new_config['xsrf_cookies'] = False  # convenient for testing...


def _create_submission() -> dict:
    survey_id = survey_table.select().where(
        survey_table.c.survey_title == 'test_title').execute().first(

    ).survey_id
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
    input_data = {'survey_id': survey_id,
                  'submitter': 'me',
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
    return api.submission.submit(input_data)['result']


class APITest(AsyncHTTPTestCase):
    def tearDown(self):
        submission_table.delete().execute()
        survey_table.delete().where(
            survey_table.c.survey_title ==
            'survey_created_through_api').execute()

    def get_app(self):
        self.app = tornado.web.Application(pages, **new_config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def testGetSubmissionsNotLoggedIn(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        response = self.fetch('/api/surveys/{}/submissions'.format(survey_id))
        self.assertEqual(response.code, 403)

    def testGetSubmissionsLoggedIn(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        _create_submission()
        with mock.patch.object(SubmissionsAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch(
                '/api/surveys/{}/submissions'.format(survey_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response,
                         api.submission.get_all(survey_id, 'test_email'))

    def testGetSubmissionsBySubmitter(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        _create_submission()
        with mock.patch.object(SubmissionsAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch(
                '/api/surveys/{}/submissions?submitter=me'.format(survey_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response,
                         api.submission.get_all(survey_id, 'test_email',
                                                submitters=['me']))

    def testGetSubmissionsWithFilter(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')

        question_id = question_table.select().where(
            and_cond).execute().first().question_id
        _create_submission()
        filters = [{'question_id': question_id, 'answer_integer': 1}]
        with mock.patch.object(SubmissionsAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch(
                '/api/surveys/{}/submissions'.format(survey_id), method='POST',
                body=json_encode({'filters': filters}))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response,
                         api.submission.get_all(survey_id, 'test_email',
                                                filters=filters))

    def testGetSubmissionsWithAPIToken(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        token_result = api.user.generate_token({'email': 'test_email'})
        token = token_result['result']['token']
        response = self.fetch('/api/surveys/{}/submissions'.format(survey_id),
                              headers={'Token': token, 'Email': 'test_email'})
        self.assertEqual(response.code, 200)
        self.assertEqual(json_decode(to_unicode(response.body)),
                         api.submission.get_all(survey_id, 'test_email'))

    def testGetSubmissionsWithoutAPIToken(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        response = self.fetch('/api/surveys/{}/submissions'.format(survey_id))
        self.assertEqual(response.code, 403)

    def testGetSubmissionsWithInvalidAPIToken(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        api.user.generate_token({'email': 'test_email'})['result']['token']
        response = self.fetch('/api/surveys/{}/submissions'.format(survey_id),
                              headers={'Token': generate_api_token(),
                                       'Email': 'test_email'})
        self.assertEqual(response.code, 403)

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
                         api.submission.get_one(submission_id, 'test_email'))

    def testPostSubmission(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
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
        input_data = {'survey_id': survey_id,
                      'submitter': 'testPostSubmissionSubmitter',
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

        token_result = api.user.generate_token({'email': 'test_email'})
        token = token_result['result']['token']

        response = self.fetch('/api/surveys/{}/submit'.format(survey_id),
                              method='POST', body=json_encode(input_data),
                              headers={'Email': 'test_email',
                                       'Token': token})
        result = json_decode(to_unicode(response.body))['result']
        submission_id = result['submission_id']
        self.assertEqual(result,
                         api.submission.get_one(submission_id,
                                                email='test_email')['result'])
        self.assertEqual(response.code, 201)

    def testGetSurveys(self):
        with mock.patch.object(SurveysAPIHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/surveys')
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response, api.survey.get_all('test_email'))

    def testGetSingleSurvey(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        with mock.patch.object(SingleSurveyAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/surveys/{}'.format(survey_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response,
                         api.survey.get_one(survey_id, email='test_email'))

    def testCreateSurvey(self):
        input_data = {'email': 'test_email',
                      'survey_title': 'survey_created_through_api',
                      'questions': [{'question_title': 'a question',
                                     'type_constraint_name': 'text',
                                     'hint': '',
                                     'allow_multiple': False,
                                     'logic': {'required': False,
                                               'with_other': False},
                                     'question_to_sequence_number': -1,
                                     'choices': None,
                                     'branches': None}]}

        token_result = api.user.generate_token({'email': 'test_email'})
        token = token_result['result']['token']

        response = self.fetch('/api/surveys/create',
                              method='POST', body=json_encode(input_data),
                              headers={'Email': 'test_email',
                                       'Token': token})
        result = json_decode(to_unicode(response.body))['result']
        survey_id = result['survey_id']
        self.assertEqual(result,
                         api.survey.get_one(survey_id,
                                            email='test_email')['result'])
        self.assertEqual(response.code, 201)

    def testGetMin(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        question_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?min'.format(question_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        min_res = api.aggregation.min(question_id, email='test_email')
        self.assertEqual(webpage_response, json_response([min_res]))

    def testGetShmin(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        question_id = question.question_id

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch(
                '/api/aggregate/{}?shmin'.format(question_id))
        self.assertEqual(response.code, 422)
        self.assertIn('no_such_method', str(response.error))

    def testGetMinInvalidType(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'text')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        question_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': question_id,
                                'answer': str(i),
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?min'.format(question_id))
        self.assertEqual(response.code, 422)
        self.assertIn('invalid_type', str(response.error))

    def testGetMinNoSubmissions(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        question_id = question.question_id

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?min'.format(question_id))
        self.assertEqual(response.code, 422)
        self.assertIn('no_submissions', str(response.error))

    def testGetMax(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        question_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?max'.format(question_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        max_res = api.aggregation.max(question_id, email='test_email')
        self.assertEqual(webpage_response, json_response([max_res]))

    def testGetMinAndMax(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        question_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch(
                '/api/aggregate/{}?min&max'.format(question_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))['result']
        self.assertNotEqual(webpage_response, [])
        self.assertIn(api.aggregation.min(question_id, email='test_email'),
                      webpage_response)
        self.assertIn(api.aggregation.max(question_id, email='test_email'),
                      webpage_response)

    def testGetSum(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        question_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?sum'.format(question_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        sum_res = api.aggregation.sum(question_id, email='test_email')
        self.assertEqual(webpage_response, json_response([sum_res]))

    def testGetCount(self):
        survey_id = survey_table.select(). \
            where(survey_table.c.survey_title == 'test_title').execute() \
            .first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        q_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?count'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response,
                         json_response([
                             api.aggregation.count(q_id, email='test_email')]))

    def testGetAvg(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        q_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?avg'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response,
                         json_response(
                             [api.aggregation.avg(q_id, email='test_email')]))

    def testGetStddevPop(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        q_id = question.question_id

        for i in range(3):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?stddev_pop'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        stddev_pop_res = api.aggregation.stddev_pop(q_id, email='test_email')
        self.assertEqual(webpage_response, json_response([stddev_pop_res]))

    def testGetStddevSamp(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        q_id = question.question_id

        for i in range(3):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?stddev_samp'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        stddev_samp_res = api.aggregation.stddev_samp(q_id, email='test_email')
        self.assertEqual(webpage_response, json_response([stddev_samp_res]))

    def testGetMode(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        q_id = question.question_id

        for i in (1, 2, 2, 3):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?mode'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response,
                         json_response(
                             [api.aggregation.mode(q_id, email='test_email')]))

    def testGetModeLocation(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'location')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        q_id = question.question_id

        input_data = {'survey_id': survey_id,
                      'submitter': 'test_submitter',
                      'answers':
                          [{'question_id': q_id,
                            'answer': [90, 0],
                            'is_other': False}]}
        api.submission.submit(input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?mode'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(webpage_response, [])
        self.assertEqual(webpage_response,
                         json_response(
                             [api.aggregation.mode(q_id, email='test_email')]))

    def testGetTimeSeries(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        q_id = question.question_id

        for i in range(3):
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?time_series'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))['result']
        self.assertNotEqual(webpage_response, [])
        api_response = api.aggregation.time_series(q_id, email='test_email')
        self.assertSequenceEqual(webpage_response[0]['result'][0],
                                 api_response['result'][0])
        self.assertSequenceEqual(webpage_response[0]['result'][1],
                                 api_response['result'][1])

    def testGetBarGraph(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        q_id = question.question_id

        for i in [0, 2, 1, 0]:
            input_data = {'survey_id': survey_id,
                          'submitter': 'test_submitter',
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(AggregationHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/aggregate/{}?bar_graph'.format(q_id))
        self.assertEqual(response.code, 200)
        webpage_response = json_decode(to_unicode(response.body))['result']
        self.assertNotEqual(webpage_response, [])
        api_response = api.aggregation.bar_graph(q_id, email='test_email')
        self.assertSequenceEqual(webpage_response[0]['result'][0],
                                 api_response['result'][0])
        self.assertSequenceEqual(webpage_response[0]['result'][1],
                                 api_response['result'][1])


class DebugTest(AsyncHTTPTestCase):
    def get_app(self):
        self.app = tornado.web.Application(pages, **new_config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def tearDown(self):
        auth_user_table.delete().where(
            auth_user_table.c.email == 'debug_test_email').execute()

    def testCreate(self):
        self.fetch('/debug/create/debug_test_email')
        self.assertIsNotNone(get_auth_user_by_email('debug_test_email'))

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
        self.app = tornado.web.Application(pages, **new_config)
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
            lambda: table.insert().values(
                type_constraint_name='text').execute(), logger=Log())
        self.assertRaises(tornado.web.HTTPError, wrapped)


class IndexTest(AsyncHTTPTestCase):
    def get_app(self):
        self.app = tornado.web.Application(pages, **new_config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def testPost(self):
        response = self.fetch('/', method='POST', body='')
        self.assertEqual(response.code, 200)


class SurveyTest(AsyncHTTPTestCase):
    def get_app(self):
        self.app = tornado.web.Application(pages, **new_config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def tearDown(self):
        submission_table.delete().execute()

    def testGetPrefix(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        response = self.fetch('/survey/{}'.format(survey_id[:35]))
        response2 = self.fetch('/survey/{}'.format(survey_id))
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, response2.body)

    def testGet(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        response = self.fetch('/survey/{}'.format(survey_id))
        self.assertEqual(response.code, 200)

    def testGet404(self):
        response = self.fetch('/survey/{}'.format(str(uuid.uuid4())))
        self.assertEqual(response.code, 404)

    def testPost(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        answer_json = {'submitter': 'me', 'survey_id': survey_id, 'answers': [
            {'question_id': get_questions_no_credentials(
                survey_id).first().question_id,
             'answer': 1,
             'is_other': False}]}
        response = self.fetch('/survey/{}'.format(survey_id), method='POST',
                              body=json_encode(answer_json))

        self.assertFalse(response.error)
        result = to_unicode(response.body)
        result_submission_id = json_decode(result)['result']['submission_id']
        condition = submission_table.c.submission_id == result_submission_id
        self.assertEqual(
            submission_table.select().where(condition).execute().rowcount, 1)
        sub_answers = get_answers(result_submission_id)
        self.assertEqual(sub_answers.rowcount, 1)

    def testPostNotJson(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        response = self.fetch('/survey/{}'.format(survey_id), method='POST',
                              body='not even close to json')

        self.assertEqual(response.code, 400)
        self.assertEqual(str(response.error),
                         'HTTP 400: {"message": "Problems parsing JSON"}')

    def testPostMissingValue(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        answer_json = {'survey_id': survey_id}
        response = self.fetch('/survey/{}'.format(survey_id), method='POST',
                              body=json_encode(answer_json))

        self.assertEqual(response.code, 422)
        self.assertIn('missing_field', str(response.error))

    def testPostWrongSurveyID(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        wrong_id = survey_table.select().where(
            survey_table.c.survey_title != 'test_title').execute().first(

        ).survey_id
        answer_json = {'survey_id': wrong_id, 'answers': [
            {'question_id': get_questions_no_credentials(
                survey_id).first().question_id,
             'answer': 1,
             'is_other': False}]}
        response = self.fetch('/survey/{}'.format(survey_id), method='POST',
                              body=json_encode(answer_json))

        self.assertEqual(response.code, 422)
        self.assertIn('invalid', str(response.error))

    def testPostWrongQuestionID(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        wrong_id = survey_table.select().where(
            survey_table.c.survey_title != 'test_title').execute().first(

        ).survey_id
        question_id = get_questions_no_credentials(
            wrong_id).first().question_id
        answers = [{'question_id': question_id,
                    'answer': 1,
                    'is_other': False}]
        answer_json = {'submitter': 'me',
                       'survey_id': survey_id,
                       'answers': answers}
        response = self.fetch('/survey/{}'.format(survey_id), method='POST',
                              body=json_encode(answer_json))

        self.assertEqual(response.code, 422)
        self.assertIn('invalid', str(response.error))


class ViewTest(AsyncHTTPTestCase):
    def tearDown(self):
        submission_table.delete().execute()

    def get_app(self):
        self.app = tornado.web.Application(pages, **config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def testGetSurveys(self):
        with mock.patch.object(ViewHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/view')
        self.assertIn('test_title', to_unicode(response.body))

    def testGetSubmissions(self):
        survey_id = survey_table.select().where(
            survey_table.c.survey_title == 'test_title').execute().first(

        ).survey_id
        _create_submission()
        with mock.patch.object(ViewSubmissionsHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/view/{}'.format(survey_id))
        self.assertIn('/view/submission/', to_unicode(response.body))

    def testGetSubmission(self):
        submission_id = _create_submission()['submission_id']
        with mock.patch.object(ViewSubmissionHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/view/submission/{}'.format(submission_id))
        self.assertIn('Answer: 3.5', to_unicode(response.body))


if __name__ == '__main__':
    unittest.main()
