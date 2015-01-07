#!/usr/bin/env python3

"""
This tornado server creates the client app by serving html/css/js and
it also functions as the wsgi container for accepting survey form post
requests back from the client app.
"""
import functools
import json

import tornado.web
import tornado.ioloop

import api.survey
import api.submission
import api.api_token
import api.user
from db.auth_user import verify_api_token
from pages.auth import LogoutHandler, LoginHandler
from pages.base import BaseHandler
from pages.debug import DebugLoginHandler, DebugLogoutHandler
import settings
from utils.logger import setup_custom_logger

from db.survey import SurveyDoesNotExistError, SurveyAlreadyExistsError


logger = setup_custom_logger('dokomo')


class Index(BaseHandler):
    def get(self, msg="Welcome"):
        current_user = ""
        if self.current_user:
            current_user = self.current_user.decode('utf-8')

        self.render('index.html', 
                message=msg + " " + current_user,  # This is temporary don't panic
                user=current_user)

    def post(self, *args):
        LogoutHandler.post(self) #TODO move to js
        self.get("You logged out")

class Survey(BaseHandler):
    def get(self, uuid):
        try:
            survey = api.survey.get_one(uuid)
            self.render('survey.html', 
                    survey=json.dumps(survey), 
                    title=survey['title'])

        except SurveyDoesNotExistError:
            Index.get(self, "Survey not found")

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


def api_authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            token = self.request.headers['Token']
            email = self.request.headers['Email']
            if not verify_api_token(token=token, email=email):
                raise tornado.web.HTTPError(403)
        return method(self, *args, **kwargs)

    return wrapper


class SurveysAPI(BaseHandler):
    @api_authenticated
    def get(self):
        surveys = api.survey.get_all(
            {'email': self.current_user.decode('utf-8')})
        self.write(json.dumps(surveys))


config = {
    'template_path': 'static',
    'static_path': 'static',
    'xsrf_cookies': True,
    'login_url': '/',
    'cookie_secret': settings.COOKIE_SECRET,
    'debug': True  # Remove this
}

pages = [  
           # Dokomo Forms
           (r'/', Index),  # Ebola front page

           # Survey Submissions
           (r'/([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})', Survey),

           # Auth
           (r'/user/login/persona/?', LoginHandler),  # Post to Persona here

           # API tokens
           (r'/user/generate-api-token/?', APITokenGenerator),

           # Testing
           (r'/api/surveys/?', SurveysAPI),
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

