#!/usr/bin/env python

"""
This tornado server creates the client app by serving html/css/js and
it also functions as the wsgi container for accepting survey form post
requests back from the client app.

"""

import tornado.web
import tornado.ioloop
import json
from db import engine
from db.answer import answer_insert
from db.submission import submission_insert
from db.survey import survey_json

import settings

from utils.logger import setup_custom_logger
logger = setup_custom_logger('dokomo')


class Index(tornado.web.RequestHandler):
    def get(self):
        # temporarily hard-coded
        survey_id = 'bcf89427-87d4-43ba-807e-9ffc8a095759'
        survey = survey_json(survey_id)
        self.render('index.html', survey=survey)

    def post(self):
        # viktor here, uuid may be absorbed into data
        uuid = self.get_argument('uuid')
        data = json.loads(self.get_argument('data'))

        survey_id = data['survey_id']
        responses = data['responses']

        submission_id = None

        with engine.begin as connection:
            submission_values = {'latitude': 0,
                                 'longitude': 0,
                                 'submitter': '',
                                 'survey_id': survey_id
                                }
            result = connection.execute(submission_insert(**submission_values))
            submission_id = result.inserted_primary_key[0]

            for answer_dict in responses:
                question_id = answer_dict['question_id']
                response = answer_dict['response']
                answer_values = {'answer': response,
                                 'question_id': question_id,
                                 'submission_id': submission_id,
                                 'survey_id': survey_id
                                }
                connection.execute(answer_insert(**answer_values))

        return submission_id



config = {
    'template_path': 'static',
    'static_path': 'static',
    'xsrf_cookies': False,
    'debug': True
}

# Good old database
# engine = create_engine(settings.CONNECTION_STRING, convert_unicode=True)

def startserver():
    """It's good practice to put all the startup logic
    in a class or function, invoked via '__main__'
    instead of just starting on import, which, among
    other things, fubars the tests"""

    app = tornado.web.Application([
        (r'/', Index)
    ], **config)
    app.listen(settings.WEBAPP_PORT, '0.0.0.0')

    logger.info('starting server on port '+str(settings.WEBAPP_PORT))

    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    startserver()
