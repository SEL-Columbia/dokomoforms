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

import api.aggregation
import api.submission
import api.survey
import api.user
from db import engine
from db.answer import get_answers
from db.auth_user import generate_api_token
from db.question import get_questions, question_table
from db.question_choice import question_choice_table
from db.submission import submission_table
from pages.api.aggregations import MinAPIHandler, MaxAPIHandler, \
    SumAPIHandler, \
    CountAPIHandler, AvgAPIHandler, StddevPopAPIHandler, \
    StddevSampAPIHandler, \
    TimeSeriesAPIHandler
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
    input_data = {'survey_id': survey_id,
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
    return api.submission.submit(input_data)


class APITest(AsyncHTTPTestCase):
    def tearDown(self):
        submission_table.delete().execute()

    def get_app(self):
        self.app = tornado.web.Application(pages, **config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def testGetSubmissionsNotLoggedIn(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        response = self.fetch('/api/surveys/{}/submissions'.format(survey_id))
        self.assertEqual(response.code, 403)

    def testGetSubmissionsLoggedIn(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        _create_submission()
        with mock.patch.object(SubmissionsAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch(
                '/api/surveys/{}/submissions'.format(survey_id))
        self.assertEqual(response.code, 200)
        json_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(json_response, [])
        self.assertEqual(json_response,
                         api.submission.get_all(survey_id, 'test_email'))

    def testGetSubmissionsWithAPIToken(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        token = api.user.generate_token({'email': 'test_email'})['token']
        response = self.fetch('/api/surveys/{}/submissions'.format(survey_id),
                              headers={'Token': token, 'Email': 'test_email'})
        self.assertEqual(response.code, 200)
        self.assertEqual(json_decode(to_unicode(response.body)),
                         api.submission.get_all(survey_id, 'test_email'))

    def testGetSubmissionsWithInvalidAPIToken(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        token = api.user.generate_token({'email': 'test_email'})['token']
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
        json_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(json_response, [])
        self.assertEqual(json_response,
                         api.submission.get_one(submission_id, 'test_email'))

    def testGetSurveys(self):
        with mock.patch.object(SurveysAPIHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/surveys')
        self.assertEqual(response.code, 200)
        json_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(json_response, [])
        self.assertEqual(json_response, api.survey.get_all('test_email'))

    def testGetSingleSurvey(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        with mock.patch.object(SingleSurveyAPIHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/surveys/{}'.format(survey_id))
        self.assertEqual(response.code, 200)
        json_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(json_response, [])
        self.assertEqual(json_response,
                         api.survey.get_one(survey_id, email='test_email'))

    def testGetMin(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        question_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(MinAPIHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/min/{}'.format(question_id))
        self.assertEqual(response.code, 200)
        json_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(json_response, [])
        self.assertEqual(json_response,
                         api.aggregation.min(question_id, email='test_email'))

    def testGetMax(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        question_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(MaxAPIHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/max/{}'.format(question_id))
        self.assertEqual(response.code, 200)
        json_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(json_response, [])
        self.assertEqual(json_response,
                         api.aggregation.max(question_id, email='test_email'))

    def testGetSum(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        question_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'answers':
                              [{'question_id': question_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(SumAPIHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/sum/{}'.format(question_id))
        self.assertEqual(response.code, 200)
        json_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(json_response, [])
        self.assertEqual(json_response,
                         api.aggregation.sum(question_id, email='test_email'))

    def testGetCount(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        q_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(CountAPIHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/count/{}'.format(q_id))
        self.assertEqual(response.code, 200)
        json_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(json_response, [])
        self.assertEqual(json_response,
                         api.aggregation.count(q_id, email='test_email'))

    def testGetAvg(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        q_id = question.question_id

        for i in range(2):
            input_data = {'survey_id': survey_id,
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(AvgAPIHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/avg/{}'.format(q_id))
        self.assertEqual(response.code, 200)
        json_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(json_response, [])
        self.assertEqual(json_response,
                         api.aggregation.avg(q_id, email='test_email'))

    def testGetStddevPop(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        q_id = question.question_id

        for i in range(3):
            input_data = {'survey_id': survey_id,
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(StddevPopAPIHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/stddev_pop/{}'.format(q_id))
        self.assertEqual(response.code, 200)
        json_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(json_response, [])
        self.assertEqual(json_response,
                         api.aggregation.stddev_pop(q_id, email='test_email'))

    def testGetStddevSamp(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        q_id = question.question_id

        for i in range(3):
            input_data = {'survey_id': survey_id,
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(StddevSampAPIHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/stddev_samp/{}'.format(q_id))
        self.assertEqual(response.code, 200)
        json_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(json_response, [])
        self.assertEqual(json_response,
                         api.aggregation.stddev_samp(q_id, email='test_email'))

    # def testGetMode(self):
    # survey_id = survey_table.select().where(
    # survey_table.c.title == 'test_title').execute().first().survey_id
    #     and_cond = and_(question_table.c.survey_id == survey_id,
    #                     question_table.c.type_constraint_name == 'integer')
    #     q_where = question_table.select().where(and_cond)
    #     question = q_where.execute().first()
    #     q_id = question.question_id
    #
    #     for i in (1, 2, 2, 3):
    #         input_data = {'survey_id': survey_id,
    #                       'answers':
    #                           [{'question_id': q_id,
    #                             'answer': i,
    #                             'is_other': False}]}
    #         api.submission.submit(input_data)
    #
    #     with mock.patch.object(ModeAPIHandler, 'get_secure_cookie') as m:
    #         m.return_value = 'test_email'
    #         response = self.fetch('/api/mode/{}'.format(q_id))
    #     self.assertEqual(response.code, 200)
    #     json_response = json_decode(to_unicode(response.body))
    #     self.assertNotEqual(json_response, [])
    #     self.assertEqual(json_response,
    #                      api.aggregation.mode(q_id, email='test_email'))

    def testGetTimeSeries(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        q_where = question_table.select().where(and_cond)
        question = q_where.execute().first()
        q_id = question.question_id

        for i in range(3):
            input_data = {'survey_id': survey_id,
                          'answers':
                              [{'question_id': q_id,
                                'answer': i,
                                'is_other': False}]}
            api.submission.submit(input_data)

        with mock.patch.object(TimeSeriesAPIHandler, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/time_series/{}'.format(q_id))
        self.assertEqual(response.code, 200)
        json_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(json_response, [])
        api_response = api.aggregation.time_series(q_id, email='test_email')
        self.assertSequenceEqual(json_response['result'][0],
                                 api_response['result'][0])
        self.assertSequenceEqual(json_response['result'][1],
                                 api_response['result'][1])


class DebugTest(AsyncHTTPTestCase):
    def get_app(self):
        self.app = tornado.web.Application(pages, **new_config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

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
            survey_table.c.title == 'test_title').execute().first().survey_id
        response = self.fetch('/survey/{}'.format(survey_id[:35]))
        response2 = self.fetch('/survey/{}'.format(survey_id))
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, response2.body)

    def testGet(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        response = self.fetch('/survey/{}'.format(survey_id))
        self.assertEqual(response.code, 200)

    def testGet404(self):
        response = self.fetch('/survey/{}'.format(str(uuid.uuid4())))
        self.assertEqual(response.code, 404)

    def testPost(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        answer_json = {'survey_id': survey_id, 'answers': [
            {'question_id': get_questions(survey_id).first().question_id,
             'answer': 1,
             'is_other': False}]}
        response = self.fetch('/survey/{}'.format(survey_id), method='POST',
                              body=json_encode(answer_json))

        self.assertFalse(response.error)
        result = to_unicode(response.body)
        result_submission_id = json_decode(result)['submission_id']
        condition = submission_table.c.submission_id == result_submission_id
        self.assertEqual(
            submission_table.select().where(condition).execute().rowcount, 1)
        sub_answers = get_answers(result_submission_id)
        self.assertEqual(sub_answers.rowcount, 1)

    def testPostNotJson(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        response = self.fetch('/survey/{}'.format(survey_id), method='POST',
                              body='not even close to json')

        self.assertEqual(response.code, 400)
        self.assertEqual(str(response.error),
                         'HTTP 400: {"message": "Problems parsing JSON"}')

    def testPostMissingValue(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        answer_json = {'survey_id': survey_id}
        response = self.fetch('/survey/{}'.format(survey_id), method='POST',
                              body=json_encode(answer_json))

        self.assertEqual(response.code, 422)
        self.assertIn('missing_field', str(response.error))

    def testPostWrongSurveyID(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        wrong_id = survey_table.select().where(
            survey_table.c.title != 'test_title').execute().first().survey_id
        answer_json = {'survey_id': wrong_id, 'answers': [
            {'question_id': get_questions(survey_id).first().question_id,
             'answer': 1,
             'is_other': False}]}
        response = self.fetch('/survey/{}'.format(survey_id), method='POST',
                              body=json_encode(answer_json))

        self.assertEqual(response.code, 422)
        self.assertIn('invalid', str(response.error))

    def testPostWrongQuestionID(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        wrong_id = survey_table.select().where(
            survey_table.c.title != 'test_title').execute().first().survey_id
        answer_json = {'survey_id': survey_id, 'answers': [
            {'question_id': get_questions(wrong_id).first().question_id,
             'answer': 1,
             'is_other': False}]}
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
            survey_table.c.title == 'test_title').execute().first().survey_id
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

