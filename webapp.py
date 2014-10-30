#!/usr/bin/env python3

"""
This tornado server creates the client app by serving html/css/js and
it also functions as the wsgi container for accepting survey form post
requests back from the client app.
"""
import json

import tornado.web
import tornado.ioloop

import api.survey
import api.submission
import settings
from utils.logger import setup_custom_logger


logger = setup_custom_logger('dokomo')


class BaseHandler(tornado.web.RequestHandler):
    """Common handler functions here (e.g. user auth, template helpers)"""


class Index(BaseHandler):
    def get(self):
        survey = api.survey.get_one(settings.SURVEY_ID)
        self.render('index.html', survey=json.dumps(survey))

    def post(self):
        data = json.loads(self.get_argument('data'))

        self.write(api.submission.submit(data))


class CreateSurvey(BaseHandler):
    def get(self):
        self.render('viktor-create-survey.html')

    def post(self):
        self.write(api.survey.create({'title': self.get_argument('title')}))


class Surveys(BaseHandler):
    def get(self):
        surveys = api.survey.get_all()
        self.write(json.dumps(surveys))

    def post(self):
        pass


class Survey(BaseHandler):
    def get(self, id):
        survey = api.survey.get_one(id)
        self.write(json.dumps(survey))
        
    def post(self, id):
        # Backward compatability for older browsers
        method = self.get_argument('_method', None)
        if method == 'DELETE':
            return self.delete(id)
        
        try:
            # Validate data
            data = json.loads(self.get_argument('data'))
            data['title']
            for question in data['questions']:
                question['title']
                question['type_constraint_name']
        except:
            raise tornado.web.HTTPError(400)
        
        survey = api.survey.create(data)
        self.write(json.dumps(survey))
        
    def delete(self, id):
        msg = api.survey.delete()
        self.write(json.dumps(msg))
        

class Submissions(BaseHandler):
    def get(self):
        submissions = api.submission.get_all()
        self.write(json.dumps(submissions))
        
    def post(self):
        pass


config = {
    'template_path': 'static',
    'static_path': 'static',
    'xsrf_cookies': False,
    'debug': True
}


if __name__ == '__main__':
    app = tornado.web.Application([
        (r'/', Index),
        (r'/surveys', Surveys),
        (r'/surveys/(.+)', Survey),
        (r'/surveys/(.+)/submissions', Submissions),
        (r'/viktor-create-survey', CreateSurvey)
    ], **config)
    app.listen(settings.WEBAPP_PORT, '0.0.0.0')

    logger.info('starting server on port ' + str(settings.WEBAPP_PORT))

    tornado.ioloop.IOLoop.current().start()

