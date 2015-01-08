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
import api.api_token
import api.user
from pages.auth import LogoutHandler, LoginHandler
from pages.api.submissions import SubmissionsAPI, SingleSubmissionAPI
from pages.api.surveys import SurveysAPI, SingleSurveyAPI
from pages.util.base import BaseHandler
from pages.debug import DebugLoginHandler, DebugLogoutHandler
import settings
from utils.logger import setup_custom_logger
from db.survey import SurveyDoesNotExistError


logger = setup_custom_logger('dokomo')


class Index(BaseHandler):

    def get(self, msg=""):
        current_user = ""
        if self.current_user:
            current_user = self.current_user.decode('utf-8')
        self.render('index.html', message=msg, user=current_user)

    def post(self, *args):
        LogoutHandler.post(self) #TODO move to js
        self.get("You logged out")


class Survey(BaseHandler):
    def get(self, survey_id: str):
        try:
            survey = api.survey.display_survey(survey_id)
            self.render('survey.html',
                        survey=json.dumps(survey),
                        title=survey['title'])

        except SurveyDoesNotExistError:
            raise tornado.web.HTTPError(404)

    def post(self, uuid):
        data = json.loads(self.request.body.decode('utf-8'))
        self.write(api.submission.submit(data))


class PageRequiringLogin(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('requires-login.html')


class APITokenGenerator(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # self.render('api-token.html')
        self.write(
            api.api_token.generate_token(
                {'email': self.current_user.decode('utf-8')}))


    @tornado.web.authenticated
    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))

        self.write(api.api_token.generate_token(data))


config = {
    'template_path': 'static',
    'static_path': 'static',
    'xsrf_cookies': True,
    'login_url': '/',
    'cookie_secret': settings.COOKIE_SECRET,
    'debug': True  # Remove this
}

uuid_regex = '[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[' \
             'a-f0-9]{12}'

pages = [
           # Dokomo Forms
           (r'/', Index),  # Ebola front page

           # Survey Submissions
           (r'/({})/?'.format(uuid_regex), Survey),

           # Auth
           (r'/user/login/persona/?', LoginHandler),  # Post to Persona here

           # API tokens
           (r'/user/generate-api-token/?', APITokenGenerator),

           # Testing
           (r'/api/surveys/?', SurveysAPI),
           (r'/api/surveys/({})/?'.format(uuid_regex), SingleSurveyAPI),
           (r'/api/surveys/({})/submissions/?'.format(uuid_regex),
            SubmissionsAPI),
           (r'/api/submissions/({})/?'.format(uuid_regex),
            SingleSubmissionAPI),
           (r'/user/requires-login/?', PageRequiringLogin),
]

if config.get('debug', False):
    pages += [(r'/debug/login/?', DebugLoginHandler),
              (r'/debug/logout/?', DebugLogoutHandler),
    ]

if __name__ == '__main__':
    app = tornado.web.Application(pages, **config)
    app.listen(settings.WEBAPP_PORT, '0.0.0.0')

    logger.info('starting server on port ' + str(settings.WEBAPP_PORT))

    tornado.ioloop.IOLoop.current().start()
