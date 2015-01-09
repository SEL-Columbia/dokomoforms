"""
Tests for the dokomo webapp

"""

import json
import unittest

import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web

from db.answer import get_answers
from db.question import get_questions
from db.submission import submission_table
import settings
from webapp import config, pages
from db.survey import survey_table


TEST_PORT = 8001 # just to show you can test the same
                 # container on a different port

POST_HDRS = {"Content-type": "application/x-www-form-urlencoded",
             "Accept": "text/plain"}

new_config = config.copy()
new_config['xsrf_cookies'] = False # convenient for testing...
# eventually we should use mock instead

class TestDokomoWebapp(unittest.TestCase):
    http_server = None
    response = None

    def setUp(self):
        application = tornado.web.Application(pages, **new_config)
        self.http_server = tornado.httpserver.HTTPServer(application)
        self.http_server.listen(TEST_PORT)

    def tearDown(self):
        self.http_server.stop()
        submission_table.delete().execute()

    def handle_request(self, response):
        self.response = response
        tornado.ioloop.IOLoop.instance().stop()

    def testGetIndex(self):
        survey_id = survey_table.select().execute().first().survey_id
        settings.SURVEY_ID = survey_id
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch( 'http://localhost:%d/' % TEST_PORT, self.handle_request)
        tornado.ioloop.IOLoop.instance().start()
        self.assertFalse(self.response.error)
        # Test contents of response
        self.assertIn(u'<title>Dokomo Forms</title>', str(self.response.body))

    def testFormPost(self):
        survey_id = survey_table.select().execute().first().survey_id
        answer_json = {'survey_id': survey_id, 'answers': [
            {'question_id': get_questions(survey_id).first().question_id,
             'answer': 1,
             'is_other': False}]}

        # prepare the POST request
        http_client = tornado.httpclient.AsyncHTTPClient()
        req = tornado.httpclient.HTTPRequest(url='http://localhost:%d/%s' % (TEST_PORT, survey_id),
                                             method='POST',
                                             headers=POST_HDRS,
                                             body=json.dumps(answer_json))
        http_client.fetch(req, self.handle_request)
        tornado.ioloop.IOLoop.instance().start()
        self.assertFalse(self.response.error)
        result = self.response.body.decode('utf-8')
        result_submission_id = json.loads(result)['submission_id']
        condition = submission_table.c.submission_id == result_submission_id
        self.assertEqual(
            submission_table.select().where(condition).execute().rowcount, 1)
        sub_answers = get_answers(result_submission_id)
        self.assertEqual(sub_answers.rowcount, 1)

if __name__ == '__main__':
    unittest.main()

