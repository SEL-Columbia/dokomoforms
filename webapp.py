#!/usr/bin/env python3

"""
This tornado server creates the client app by serving html/css/js and
it also functions as the wsgi container for accepting survey form post
requests back from the client app.
"""
from tornado.escape import to_unicode, json_encode, json_decode
import tornado.web
import tornado.ioloop

import api.survey
import api.submission
import api.user
from pages.auth import LogoutHandler, LoginHandler
from pages.api.submissions import SubmissionsAPI, SingleSubmissionAPI
from pages.api.surveys import SurveysAPI, SingleSurveyAPI
from pages.util.base import BaseHandler
import pages.util.ui
from pages.debug import DebugLoginHandler, DebugLogoutHandler
import settings
from utils.logger import setup_custom_logger
from db.survey import SurveyPrefixDoesNotIdentifyASurvey


logger = setup_custom_logger('dokomo')


class Index(BaseHandler):
    def get(self, msg=""):
        self.render('index.html', message=msg)

    def post(self):
        LogoutHandler.post(self)  # TODO move to js
        self.get("You logged out")


class Survey(BaseHandler):
    def get(self, survey_prefix: str):
        try:
            survey = api.survey.display_survey(survey_prefix)
            self.render('survey.html',
                        survey=json_encode(survey),
                        title=survey['title'])
        except SurveyPrefixDoesNotIdentifyASurvey:
            raise tornado.web.HTTPError(404)


    def post(self, uuid):
        data = json_decode(to_unicode(self.request.body))
        self.write(api.submission.submit(data))


class APITokenGenerator(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # self.render('api-token.html')
        self.write(
            api.user.generate_token(
                {'email': to_unicode(self.current_user)}))


    @tornado.web.authenticated
    def post(self):
        data = json_decode(to_unicode(self.request.body))

        self.write(api.user.generate_token(data))


config = {
    'template_path': 'static',
    'static_path': 'static',
    'xsrf_cookies': True,
    'login_url': '/',
    'cookie_secret': settings.COOKIE_SECRET,
    'ui_methods': pages.util.ui,
    'debug': True  # Remove this
}

UUID_REGEX = '[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[' \
             'a-f0-9]{12}'

pages = [
    # Dokomo Forms
    (r'/', Index),  # Ebola front page

    # Survey Submissions
    (r'/survey/(.*)/?', Survey),

    # Auth
    (r'/user/login/persona/?', LoginHandler),  # Post to Persona here

    # API tokens
    (r'/user/generate-api-token/?', APITokenGenerator),

    # Testing
    (r'/api/surveys/?', SurveysAPI),
    (r'/api/surveys/({})/?'.format(UUID_REGEX), SingleSurveyAPI),
    (r'/api/surveys/({})/submissions/?'.format(UUID_REGEX),
     SubmissionsAPI),
    (r'/api/submissions/({})/?'.format(UUID_REGEX),
     SingleSubmissionAPI),
]

if config.get('debug', False):
    pages += [(r'/debug/login/?', DebugLoginHandler),
              (r'/debug/logout/?', DebugLogoutHandler),
    ]

app = tornado.web.Application(pages, **config)

if __name__ == '__main__':
    app.listen(settings.WEBAPP_PORT, '0.0.0.0')

    logger.info('starting server on port ' + str(settings.WEBAPP_PORT))

    tornado.ioloop.IOLoop.current().start()
