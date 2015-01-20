"""
Tests for the dokomo webapp

"""

import unittest
from unittest import mock
from sqlalchemy import and_
from urllib.parse import urlencode
import uuid
from sqlalchemy import Table, MetaData

from tornado.escape import to_unicode, json_encode, json_decode
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
from tornado.testing import AsyncHTTPTestCase
import tornado.web

import api.submission
import api.survey
import api.user
from db import engine
from db.answer import get_answers
from db.auth_user import generate_api_token
from db.question import get_questions, question_table
from db.question_choice import question_choice_table
from db.submission import submission_table
from pages.api.submissions import SubmissionsAPI, SingleSubmissionAPI
from pages.api.surveys import SurveysAPI, SingleSurveyAPI
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


def create_test_submission() -> dict:
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
        create_test_submission()
        with mock.patch.object(SubmissionsAPI, 'get_secure_cookie') as m:
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
        submission_id = create_test_submission()['submission_id']
        with mock.patch.object(SingleSubmissionAPI, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/submissions/{}'.format(submission_id))
        self.assertEqual(response.code, 200)
        json_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(json_response, [])
        self.assertEqual(json_response,
                         api.submission.get_one(submission_id, 'test_email'))

    def testGetSurveys(self):
        with mock.patch.object(SurveysAPI, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/surveys')
        self.assertEqual(response.code, 200)
        json_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(json_response, [])
        self.assertEqual(json_response, api.survey.get_all('test_email'))

    def testGetSingleSurvey(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        with mock.patch.object(SingleSurveyAPI, 'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/api/surveys/{}'.format(survey_id))
        self.assertEqual(response.code, 200)
        json_response = json_decode(to_unicode(response.body))
        self.assertNotEqual(json_response, [])
        self.assertEqual(json_response,
                         api.survey.get_one(survey_id, email='test_email'))


class DebugTest(AsyncHTTPTestCase):
    def get_app(self):
        self.app = tornado.web.Application(pages, **new_config)
        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def testLoginGet(self):
        response = self.fetch('/debug/login')
        self.assertEqual(response.code, 200)

    def testLogin(self):
        response = self.fetch('/debug/login', method='POST',
                              body=urlencode({'email': 'test_email'}))
        self.assertIn('test_email', to_unicode(response.body))

    def testLoginFail(self):
        response = self.fetch('/debug/login', method='POST',
                              body=urlencode({'email': 'nope'}))
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
        answer_json = {'submitter': 'me', 'survey_id': survey_id, 'answers': [
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
        answer_json = {'submitter': 'me',
                       'survey_id': survey_id, 'answers': [
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
        create_test_submission()
        with mock.patch.object(ViewSubmissionsHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/view/{}'.format(survey_id))
        self.assertIn('/view/submission/', to_unicode(response.body))

    def testGetSubmission(self):
        survey_id = survey_table.select().where(
            survey_table.c.title == 'test_title').execute().first().survey_id
        submission_id = create_test_submission()['submission_id']
        with mock.patch.object(ViewSubmissionHandler,
                               'get_secure_cookie') as m:
            m.return_value = 'test_email'
            response = self.fetch('/view/submission/{}'.format(submission_id))
        self.assertIn('Answer: 3.5', to_unicode(response.body))


if __name__ == '__main__':
    unittest.main()

