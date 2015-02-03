#!/usr/bin/env python3

"""
This tornado server creates the client app by serving html/css/js and
it also functions as the wsgi container for accepting survey form post
requests back from the client app.
"""

from tornado.escape import json_encode
import tornado.web
import tornado.ioloop

import api.aggregation
import api.survey
import api.submission
import api.user
from pages.api.aggregations import AggregationHandler
from pages.auth import LogoutHandler, LoginHandler
from pages.api.submissions import SubmissionsAPIHandler, \
    SingleSubmissionAPIHandler, SubmitAPIHandler
from pages.api.surveys import SurveysAPIHandler, SingleSurveyAPIHandler
from pages.util.base import BaseHandler, get_json_request_body, \
    validation_message, catch_bare_integrity_error
import pages.util.ui
from pages.debug import DebugLoginHandler, DebugLogoutHandler
from pages.view.surveys import ViewHandler
from pages.view.submissions import ViewSubmissionsHandler, \
    ViewSubmissionHandler
import settings
from utils.logger import setup_custom_logger
from db.survey import SurveyPrefixDoesNotIdentifyASurveyError, \
    SurveyPrefixTooShortError, \
    get_survey_id_from_prefix, get_surveys_by_email, IncorrectQuestionIdError


logger = setup_custom_logger('dokomo')


class Index(BaseHandler):
    def get(self, msg=""):
        surveys = get_surveys_by_email(self.current_user, 10)
        self.render('index.html', message=msg, surveys=surveys)

    def post(self):
        LogoutHandler.post(self)  # TODO move to js
        self.get("You logged out")


class Survey(BaseHandler):
    def get(self, survey_prefix: str):
        try:
            survey_id = get_survey_id_from_prefix(survey_prefix)
            if len(survey_prefix) < 36:
                self.redirect('/survey/{}'.format(survey_id), permanent=False)
            else:
                survey = api.survey.display_survey(survey_id)['result']
                self.render('survey.html',
                            survey=json_encode(survey),
                            survey_title=survey['survey_title'])
        except (SurveyPrefixDoesNotIdentifyASurveyError,
                SurveyPrefixTooShortError):
            raise tornado.web.HTTPError(404)


    def post(self, uuid):
        SubmitAPIHandler.post(self, uuid) # TODO: Hey Abdi kill this


class APITokenGenerator(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # self.render('api-token.html')
        self.write(
            api.user.generate_token(
                {'email': self.current_user}))


    @tornado.web.authenticated
    def post(self):
        data = get_json_request_body(self)
        self.write(api.user.generate_token(data))


config = {
    'template_path': 'templates',
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
    (r'/', Index),

    # View surveys and submissions
    (r'/view/?', ViewHandler),
    (r'/view/({})/?'.format(UUID_REGEX), ViewSubmissionsHandler),
    (r'/view/submission/({})/?'.format(UUID_REGEX), ViewSubmissionHandler),

    # Survey Submissions
    (r'/survey/(.+)/?', Survey),

    # Auth
    (r'/user/login/persona/?', LoginHandler),  # Post to Persona here

    # API tokens
    (r'/user/generate-api-token/?', APITokenGenerator),

    # Testing
    (r'/api/aggregate/({})/?'.format(UUID_REGEX), AggregationHandler),

    (r'/api/surveys/?', SurveysAPIHandler),
    (r'/api/surveys/({})/?'.format(UUID_REGEX), SingleSurveyAPIHandler),
    (r'/api/surveys/({})/submit/?'.format(UUID_REGEX), SubmitAPIHandler),
    (r'/api/surveys/({})/submissions/?'.format(UUID_REGEX),
     SubmissionsAPIHandler),
    (r'/api/submissions/({})/?'.format(UUID_REGEX),
     SingleSubmissionAPIHandler),
]

if config.get('debug', False):
    pages += [(r'/debug/login/(.+)/?', DebugLoginHandler),
              (r'/debug/logout/?', DebugLogoutHandler),
    ]

app = tornado.web.Application(pages, **config)

if __name__ == '__main__':
    app.listen(settings.WEBAPP_PORT, '0.0.0.0')

    logger.info('starting server on port ' + str(settings.WEBAPP_PORT))

    tornado.ioloop.IOLoop.current().start()
